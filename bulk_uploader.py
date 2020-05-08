import argparse
import json
import urllib3


def authenticate(email, password):
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "password": password
    }

    data = json.dumps(payload).encode('utf-8')

    print(data)

    host = "auth.apoweroftrance.com"
    api_request = "/v1/user/authenticate"

    https = urllib3.HTTPConnectionPool(host)

    response = https.request(
        'POST', "http://%s%s" % (host, api_request),
        headers=header,
        body=data
    )
    response.read()

    # data = json.loads(response.data.decode())
    print(response.data)

    # return data["payload"]["token"]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A Power of Trance Music Uploader")
    parser.add_argument("--email", required=False, help="User Email")
    parser.add_argument("--password", required=False, help="User Password")
    parser.add_argument("--directory", required=False, help="Target Directory for Upload")

    args = parser.parse_args()

    if args.email is None:
        print("user 'email' is required")
        exit()

    if args.password is None:
        print("user 'password' is required")
        exit()

    if args.directory is None:
        print("target 'directory' is required")
        exit()

    token = authenticate(args.email, args.password)

    print(token)
