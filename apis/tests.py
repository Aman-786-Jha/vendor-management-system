from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from vendor_models.models import *

User = get_user_model()

class LoginViewTests(APITestCase):
    
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.login_url = reverse('login')
    
    def test_login_success(self):
        # Test login with valid credentials
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('responseData', response.data)
        self.assertIn('refresh', response.data['responseData'])
        self.assertIn('access', response.data['responseData'])
    
    def test_login_failure(self):
        # Test login with invalid credentials
        data = {
            'email': 'wronguser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('responseData', response.data)
        self.assertIn('non_field_errors', response.data['responseData'])



class BuyerCreateViewTests(APITestCase):
    
    def setUp(self):
        self.create_buyer_url = reverse('buyer-create')
        self.user_data = {
            'user_type': 'buyer',
            'name': 'Test Buyer',
            'email': 'testbuyer@example.com',
            'contact_details': '1234567890',
            'address': '123 Test Street',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }
    
    def test_create_buyer_success(self):
        # Test successful buyer creation
        response = self.client.post(self.create_buyer_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('responseData', response.data)
        self.assertEqual(response.data['responseMessage'], 'Buyer created successfully.')
    
    def test_create_buyer_existing_email(self):
        # Test buyer creation with an already registered email
        VendorManagementUser.objects.create_user(
            user_type='buyer',
            name='Existing User',
            email='testbuyer@example.com',
            password='testpassword123',
            address='123 Test Street',
            contact_details='1234567890'
        )
        response = self.client.post(self.create_buyer_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('responseMessage', response.data)
        self.assertEqual(response.data['responseMessage']['email'][0], 'This email has already been registered.')
    
    def test_create_buyer_password_mismatch(self):
        # Test buyer creation with mismatched passwords
        self.user_data['confirm_password'] = 'differentpassword'
        response = self.client.post(self.create_buyer_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('responseMessage', response.data)
        self.assertEqual(response.data['responseMessage']['non_field_errors'][0], 'Password does not match.')



class VendorListViewTests(APITestCase):
    
    def setUp(self):
        self.list_url = reverse('vendor-list')
        self.user = User.objects.create_user(
            user_type='vendor',
            name='Vendor User',
            email='vendoruser@example.com',
            password='vendorpassword123',
            address='123 Vendor Street',
            contact_details='1234567890'
        )
        self.vendor = Vendor.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_vendor_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('responseData', response.data)
        self.assertEqual(response.data['responseMessage'], 'Vendors retrieved successfully.')
        self.assertEqual(len(response.data['responseData']), 1)
    
    def test_get_vendor_list_with_name_filter(self):
        response = self.client.get(self.list_url, {'name': 'Vendor User'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('responseData', response.data)
        self.assertEqual(response.data['responseMessage'], 'Vendors retrieved successfully.')
        self.assertEqual(len(response.data['responseData']), 1)
    
    def test_get_vendor_list_with_email_filter(self):
        response = self.client.get(self.list_url, {'email': 'vendoruser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('responseData', response.data)
        self.assertEqual(response.data['responseMessage'], 'Vendors retrieved successfully.')
        self.assertEqual(len(response.data['responseData']), 1)
    
    def test_get_vendor_list_with_no_match(self):
        response = self.client.get(self.list_url, {'name': 'Nonexistent Vendor'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('responseData', response.data)
        self.assertEqual(response.data['responseMessage'], 'No data found')
        self.assertEqual(len(response.data['responseData']), 0)

    def test_get_vendor_list_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('responseMessage', response.data)
        self.assertEqual(response.data['responseMessage'], 'Authentication credentials were not provided.')



class VendorDetailViewTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            user_type='vendor',
            name='Vendor User',
            email='vendoruser@example.com',
            password='vendorpassword123',
            address='123 Vendor Street',
            contact_details='1234567890'
        )
        self.vendor = Vendor.objects.create(user=self.user, vendor_code='V_1_ABCD')
        self.client.force_authenticate(user=self.user)
        self.detail_url = reverse('vendor-detail', kwargs={'vendor_code': self.vendor.vendor_code})

    def test_get_vendor_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('responseData', response.data)
        self.assertEqual(response.data['responseMessage'], 'Vendor details retrieved successfully.')
        self.assertEqual(response.data['responseData']['user']['email'], self.user.email)
    
    def test_get_vendor_detail_invalid_code_format(self):
        invalid_url = reverse('vendor-detail', kwargs={'vendor_code': 'invalid_code'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('responseMessage', response.data)
        self.assertEqual(response.data['responseMessage'], 'Invalid input')
    
    def test_get_vendor_detail_not_found(self):
        not_found_url = reverse('vendor-detail', kwargs={'vendor_code': 'V_9999_ZZZZ'})
        response = self.client.get(not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('responseMessage', response.data)
        self.assertEqual(response.data['responseMessage'], 'Vendor not found.')
    
    def test_get_vendor_detail_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('responseMessage', response.data)
        self.assertEqual(response.data['responseMessage'], 'Authentication credentials were not provided.')


class VendorUpdateViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            user_type='vendor',
            name='Vendor User',
            email='vendoruser@example.com',
            password='vendorpassword123',
            address='123 Vendor Street',
            contact_details='1234567890'
        )
        self.vendor = Vendor.objects.create(user=self.user, vendor_code='V_1_ABCD')
        self.client.force_authenticate(user=self.user)
        self.update_url = reverse('vendor-update', kwargs={'vendor_code': self.vendor.vendor_code})

    def test_update_vendor_success(self):
        update_data = {
            'name': 'Updated Vendor User',
            'password': 'newpassword123',
            'address': '456 Updated Street',
            'contact_details': '0987654321'
        }
        response = self.client.put(self.update_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseMessage'], 'Vendor updated successfully.')
        self.assertEqual(response.data['responseData']['name'], update_data['name'])
    
    def test_update_vendor_invalid_code_format(self):
        invalid_url = reverse('vendor-update', kwargs={'vendor_code': 'invalid_code'})
        update_data = {
            'name': 'Updated Vendor User',
            'password': 'newpassword123',
            'address': '456 Updated Street',
            'contact_details': '0987654321'
        }
        response = self.client.put(invalid_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['responseMessage'], 'Invalid input')
    
    def test_update_vendor_not_found(self):
        not_found_url = reverse('vendor-update', kwargs={'vendor_code': 'V_9999_ZZZZ'})
        update_data = {
            'name': 'Updated Vendor User',
            'password': 'newpassword123',
            'address': '456 Updated Street',
            'contact_details': '0987654321'
        }
        response = self.client.put(not_found_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['responseMessage'], 'Vendor not found.')
    
    def test_update_vendor_invalid_data(self):
        invalid_data = {
            'name': 'Updated Vendor User',
            'password': 'short',
            'address': '456 Updated Street',
            'contact_details': '0987654321'
        }
        response = self.client.put(self.update_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['responseMessage'])
        self.assertEqual(response.data['responseMessage']['password'][0], 'Password must be at least 8 characters long.')

    def test_update_vendor_unauthenticated(self):
        self.client.logout()
        update_data = {
            'name': 'Updated Vendor User',
            'password': 'newpassword123',
            'address': '456 Updated Street',
            'contact_details': '0987654321'
        }
        response = self.client.put(self.update_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['responseMessage'], 'Authentication credentials were not provided.')


class VendorDeleteViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            user_type='vendor',
            name='Vendor User',
            email='vendoruser@example.com',
            password='vendorpassword123',
            address='123 Vendor Street',
            contact_details='1234567890'
        )
        self.vendor = Vendor.objects.create(user=self.user, vendor_code='V_1_ABCD')
        self.client.force_authenticate(user=self.user)
        self.delete_url = reverse('vendor-delete', kwargs={'vendor_code': self.vendor.vendor_code})

    def test_delete_vendor_success(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseMessage'], 'Vendor deleted successfully.')
        self.assertFalse(Vendor.objects.filter(vendor_code=self.vendor.vendor_code).exists())
        self.assertFalse(User.objects.filter(email=self.user.email).exists())
    
    def test_delete_vendor_invalid_code_format(self):
        invalid_url = reverse('vendor-delete', kwargs={'vendor_code': 'invalid_code'})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['responseMessage'], 'Invalid input')
    
    def test_delete_vendor_not_found(self):
        not_found_url = reverse('vendor-delete', kwargs={'vendor_code': 'V_9999_ZZZZ'})
        response = self.client.delete(not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['responseMessage'], 'Vendor not found.')

    def test_delete_vendor_unauthenticated(self):
        self.client.logout()
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['responseMessage'], 'Authentication credentials were not provided.')
