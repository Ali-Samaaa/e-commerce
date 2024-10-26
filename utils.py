from kavenegar import *


def send_opt_code(phone_number, code):
    try:
        api = KavenegarAPI('{code}')
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
