from datetime import timedelta


DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "salesync-rds.cunzt8irsgv8.ap-northeast-2.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "dev-sale"


SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
    user=DB_USER,
    pw=DB_PASSWORD,
    url=DB_HOST,
    port=DB_PORT,
    db=DB_NAME)


SECRET_KEY = "b'\xa2\xa4A\x84\x9f\x86\x82\x05G\xe2\xb2eD\x18p\x01'"
JWT_SECRET_KEY = b'\xb4\xc4\x8b\xfbU\xc1\x8d\x1d\x82\xca\x08^\x0bO\x05I'
JWT_DECODE_ALGORITHMS = ['HS256']
JWT_TOKEN_LOCATION = ['headers']
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)
JWT_COOKIE_SECURE = False
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
JWT_CSRF_CHECK_FORM = True
JWT_CSRF_IN_COOKIES = True
