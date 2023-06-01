from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, HTTPException, Header, Request, status
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication

app = FastAPI()

#  --- fake database
db = {
    'users': [
        {'id': 1, 'username': 'ian', 'api_key': 'secret-1234'},
        {'id': 2, 'username': 'orest', 'api_key': 'secret-7890'},
    ],
    'jokes': [
        {'id': 1, 'user_id': 1, 'joke': "Did you hear about the amateur poet who was rejected from the writing contest? It was for PROSE only."},
        {'id': 2, 'user_id': 2, 'joke': "My wife threatened to slam my head on the keyboard if I didn't get off the computer, but I'm sure she's only kiddinwihet;o2hq4qgo8hqth'o"}
    ]
}

# --- helper functions

async def get_next_id_in_janky_way():
    max_id = 0
    for joke in db['jokes']:
        if joke['id'] > max_id:
            max_id = joke['id']
    return max_id+1

async def find_item_by_id(item_id):
    for item in db['jokes']:
        if item['id'] == item_id:
            return item
    return None

async def whoami(api_key):
    result = None
    for item in db['users']:
        if 'api_key' in item and item['api_key'] == api_key:
            result = item
            break
    return result

async def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if not await whoami(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )

# --- endpoints

@app.get('/items/{item_id}', dependencies=[Depends(api_key_auth)])
async def read_item(item_id: int):
    item = await find_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Item not found'
            )
    return {'data': item}


@app.post('/items', dependencies=[Depends(api_key_auth)])
async def create_item(item: dict, request: Request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.split('Bearer ')[1]
    user = await whoami(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Not authorized'
            )
    print(1)
    if 'data' in item:
        next_id = await get_next_id_in_janky_way()
        db['jokes'].append({
            'id': next_id,
            'user_id': user['id'],
            'joke': item['data']
        })
        payload = {'data': {'id': next_id, 'joke': item['data']}}
        return payload
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Payload missing a required "data" parameter'
            )
