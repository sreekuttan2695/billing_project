from django.utils.deprecation import MiddlewareMixin

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.COOKIES.get('access_token')
        username = request.COOKIES.get('username')
        client_id = request.COOKIES.get('client_id')
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        request.client_id = client_id
        request.username = username
