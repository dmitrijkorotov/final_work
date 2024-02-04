import requests
import json
import yadisk
from datetime import datetime
from tqdm import tqdm


class Loading_photos:
    """
    A class representing a program for uploading photos from vk
    and saving them to yandex.disk.

    Attributes:
    - token_vk: str - vk token with access to photos
    - token_ya: str - yandex.disk OAuth token
    - id_user: int - vk user id

    """

    def __init__(self, token_vk, token_ya, id_user):
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.id_user = id_user

    def get_common_params(self):
        return {
            'access_token': self.token_vk,
            'v': '5.131'
        }
    
    def __get_profile_photos(self):
        url = 'https://api.vk.com/method'
        params = self.get_common_params()
        params.update({'owner_id': self.id_user,
                       'album_id': 'profile',
                       'extended': 1
                       })
        response = requests.get(f'{url}/photos.get', params=params)
        likes = [like.get('likes').get('count')
                 for like in response.json().get('response').get('items')]
        names = []
        url_photos =[]
        for item in response.json().get('response').get('items'):
            if likes.count(item.get('likes').get('count')) == 1:
                names.append(str(item.get('likes').get('count')))
            else:
                like = item.get('likes').get('count')
                date = datetime.fromtimestamp(item.get('date'))
                format_date = date.strftime('%d-%m-%Y')
                names.append(f'{like}_{format_date}')
            for url_photo in item.get('sizes'):
                if url_photo.get('type') == 'w':
                    url_photos.append(url_photo.get('url'))
        return zip(names, url_photos)
    
    def sending_photos(self, quantity=5):
        """
        Saves the specified number of photos to yandex.disk.

        Parameters:
        quantity: int, optional - the number of saved photos.
        Default is 5.

        """

        yandex_obj = yadisk.YaDisk(token=self.token_ya)
        if not yandex_obj.is_dir('/photos'):
            yandex_obj.mkdir('/photos')
        result = []
        for name, url in tqdm(list(self.__get_profile_photos())[:quantity]):
            yandex_obj.upload_url(url, f'/photos/{name}.jpg')
            report = {"file_name": f'{name}.jpg', "size": 'w'}
            result.append(report)
        
        with open('file_result.json', 'w') as f:
            json.dump(result, f, indent=1)

profile = Loading_photos()
profile.sending_photos()

    
