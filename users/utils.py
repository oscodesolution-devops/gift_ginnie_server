import requests

base_url = " https://cpaas.messagecentral.com"


def get_auth_token(
    country_code,
    phone_number,
    message_central_customer_id,
    message_central_password_key,
):
    token_url = (
        base_url
        + "/auth/v1/authentication/token?customerId="
        + message_central_customer_id
        + "&scope=NEW"
        + "&key="
        + message_central_password_key
        + "&country="
        + (country_code)
    )
    print(token_url)
    try:
        reponse = requests.get(token_url)
        print(reponse.json())
        if reponse.status_code == 200 or reponse.status_code == 201:
            token = reponse.json()["token"]
            return token
        else:
            print("Error in getting token")
            return False
    except Exception as e:
        print(e)
        return False


def send_otp(
    country_code,
    phone_number,
    message_central_customer_id,
    message_central_password_key,
):
    try:
        token = get_auth_token(
            country_code,
            phone_number,
            message_central_customer_id,
            message_central_password_key,
        )
        print(token)
        if token == False:
            return False
        elif token != False:
            otp_url = (
                base_url
                + f"/verification/v3/send?countryCode={country_code}&flowType=SMS&mobileNumber={phone_number}&otpLength=6"
            )
            print(otp_url)
            headers = {
                "authToken": token,
            }
            response = requests.post(otp_url, headers=headers)
            print(response.json())
            if response.status_code == 200:
                return {
                    "verificationId": response.json()["data"]["verificationId"],
                    "authToken": token,
                }
            elif response.status_code == 506:
                return {
                    "status": 506,
                    "verificationId": response.json()["data"]["verificationId"],
                }

            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False


def verify_otp(verification_id, otp, token):
    validate_url = (
        base_url
        + f"/verification/v3/validateOtp?verificationId={verification_id}&code={otp}"
    )
    print(validate_url)
    try:
        if token != False:
            headers = {
                "authToken": token,
            }
            response = requests.get(validate_url, headers=headers)
            print(response.json())
            if response.status_code == 200:
                return True
            elif response.status_code == 702:
                return False
            else:
                return False
        else:
            return False

    except Exception as e:
        print(e)
        return False
