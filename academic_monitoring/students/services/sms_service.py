import requests

FAST2SMS_API_KEY = "J39RsgSMopVlac6iXxuKOWEmH7B2NPdy4ArCIeq58LTGwfkYv0PlqSGnC0VwRvzbXMyFZ6c7sOemjpLx"


def send_sms(phone, message):

    # CLEAN NUMBER (VERY IMPORTANT)
    phone = str(phone).strip()
    phone = phone.replace("+91", "")
    phone = phone.replace(" ", "")

    if len(phone) != 10:
        print("Invalid phone:", phone)
        return False

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": phone
    }

    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        print("SMS RESPONSE:", response.text)
        return True

    except Exception as e:
        print("SMS ERROR:", e)
        return False
