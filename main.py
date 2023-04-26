from fastapi import FastAPI 
app = FastAPI()
from app.db import create_tables
from schema import User ,UserDB,Follower,FollowerDB

create_tables()

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_followers(followers, profile_id):
    conn = sqlite3.connect("query.db")
    c = conn.cursor()

    for follower in followers:
        name = follower["name"]
        screen_name = follower["screen_name"]
        follower_count = follower["follower_count"]
        c.execute(
            """
            INSERT INTO follower (twitter_profile_id, name, screen_name, follower_count)
            VALUES (?, ?, ?, ?)
            """,
            (profile_id, name, screen_name, follower_count)
        )

    conn.commit()
    conn.close()




def get_user_by_username(username: str) -> User:
    """Get user by username from the database"""
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=?", (username,))
    user_data = c.fetchone()

    if user_data:
        user = User(*user_data)
    else:
        user = None

    conn.close()

    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/signup")
def signup(user: User, db: Session = Depends(get_db)):
    hashed_password = hash_context.hash(user.password)

    query = "INSERT INTO user (email, hashed_password) VALUES (?, ?)"
    try:
        db.execute(query, (user.email, hashed_password))
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not security.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = security.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}





@app.post("/connect-twitter")
async def connect_twitter(credentials: TwitterCredentials, token: str = Depends(get_current_user)):
    T = tweepy.Client(
        consumer_key=credentials.consumer_key,
        consumer_secret=credentials.consumer_secret,
        access_token=credentials.access_token,
        access_token_secret=credentials.access_token_secret,
        bearer_token=credentials.bearer_token
    )

    followers = await T.get_followers()
    screen_names = [follower.screen_name for follower in followers]

    add_followers(screen_names, token.id)

    return {"message": "Followers added successfully"}




@app.get("/followers")
async def get_followers(token: str = Depends(get_current_user)):
    followers = get_followers(token.id)

    return {"followers": followers}




@app.post("/follow")
async def follow_user(request: Request, user: FollowUser, token: str = Depends(get_current_user)):
    db_user = get_user_by_username(user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    T = tweepy.Client(
        consumer_key=request.app.state.config["twitter"]["consumer_key"],
        consumer_secret=request.app.state.config["twitter"]["consumer_secret"],
        access_token=request.app.state.config["twitter"]["access_token"],
        access_token_secret=request.app.state.config["twitter"]["access_token_secret"],
        bearer_token=request.app.state.config["twitter"]["bearer_token"]
    )
    await T.create_friendship(db_user.username)

    add_follower(db_user.id, token.id)

    return {"message": "User followed successfully"}


