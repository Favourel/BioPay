import requests
from requests.exceptions import RequestException
from django.contrib.auth.backends import ModelBackend
from users.models import User
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


class UniversityAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.debug(f"Attempting authentication for user: {username}")
        # Make a request to the university's authentication API
        auth_url = 'https://portal.unilorin.edu.ng/api/login'
        payload = {'username': username, 'password': password}

        try:
            response = requests.post(auth_url, data=payload)

            response_data = response.json()

            if response.status_code == 200:

                # Authentication successful, retrieve user data
                user_data = response_data['data']
                user_model = get_user_model()

                # Retrieve other data
                department_name = user_data['department']
                role_name = user_data['role_names']
                print(role_name)

                # Check if user exists in our system, if not create a new one
                user, created = user_model.objects.get_or_create(username=username,
                                                                 )
                if created:
                    user.email = user_data.get('email', '')
                    user.first_name = user_data.get('firstname', '')
                    user.last_name = user_data.get('lastname', '')
                    user.phone_number = user_data.get('phone', '')
                    user.picture_url = user_data.get('picture_url', '')
                    user.department = department_name.get('name', '')
                    user.status = role_name[0]
                    user.save()

                return user
            else:
                raise RequestException(
                    "Authentication failed with status code: " + str(response.status_code))  # Raise exception

        except requests.exceptions.HTTPError as http_err:

            logging.error(f"HTTP error occurred: {http_err}")

            print(f"Authentication failed: {http_err}")

            return None
        except requests.exceptions.ConnectionError as conn_err:

            logging.error(f"Error connecting to the server: {conn_err}")

            print(f"Authentication failed: {conn_err}")

            return None
        except requests.exceptions.Timeout as timeout_err:

            logging.error(f"Timeout error occurred: {timeout_err}")

            print(f"Authentication failed: {timeout_err}")

            return None
        except requests.exceptions.RequestException as req_err:

            logging.error(f"Network-related error occurred: {req_err}")

            print(f"Authentication failed: {req_err}")

            return None

        except Exception as e:

            logging.error(f"An unexpected error occurred: {e}")

            print(f"Authentication failed: {str(e)}")

            return None
