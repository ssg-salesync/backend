from datetime import timedelta


DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "salesync-rds.cunzt8irsgv8.ap-northeast-2.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "salesync"


SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
    user=DB_USER,
    pw=DB_PASSWORD,
    url=DB_HOST,
    port=DB_PORT,
    db=DB_NAME)


# python -c 'import os; print(os.urandom(16))'
SECRET_KEY = "b'\xa2\xa4A\x84\x9f\x86\x82\x05G\xe2\xb2eD\x18p\x01'"
# JWT secret key
JWT_SECRET_KEY = b'\xb4\xc4\x8b\xfbU\xc1\x8d\x1d\x82\xca\x08^\x0bO\x05I'
# Type of algorithm
JWT_DECODE_ALGORITHMS = ['HS256']
# Location to check when validate JWT token
JWT_TOKEN_LOCATION = ['headers']
# JWT Access token expiration
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
# JWT refresh token expiration
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)
# If not production, off secure
JWT_COOKIE_SECURE = False
# CSRF protection
JWT_COOKIE_CSRF_PROTECT = True
# Check CSRF of method
JWT_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
# Check CSRF of forms
JWT_CSRF_CHECK_FORM = True
# Check CSRF in cookies
JWT_CSRF_IN_COOKIES = True
