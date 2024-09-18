from kavenegar import *


def send_opt_code(phone_number, code):
    try:
        api = KavenegarAPI('4145385A7A3661704746346D73475630456151693145696F4B4A587148774259464733536E6C377743776F3D')
        params = {
            'sender': '',
            'receptor': phone_number,
            'message': f'کد شما: {code}'
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
