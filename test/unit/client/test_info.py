from lib.utils.constants import AuthMode
from lib.client.info import (
    ASPrivilege,
    ASResponse,
    add_privileges,
    authenticate_new,
    change_password,
    create_role,
    create_user,
    delete_privileges,
    delete_role,
    delete_whitelist,
    drop_user,
    grant_roles,
    login,
    query_roles,
    query_users,
    revoke_roles,
    set_password,
    set_whitelist,
)
import unittest2 as unittest
from mock import Mock, patch
from socket import error as SocketError


class ASPrivilegeTest(unittest.TestCase):
    def test_str_to_enum(self):
        self.assertEqual(ASPrivilege.str_to_enum("USER-admin"), ASPrivilege.USER_ADMIN)
        self.assertEqual(ASPrivilege.str_to_enum("sys_ADMIN"), ASPrivilege.SYS_ADMIN)
        self.assertEqual(ASPrivilege.str_to_enum(""), ASPrivilege.ERROR)
        self.assertEqual(ASPrivilege.str_to_enum("read"), ASPrivilege.READ)
        self.assertEqual(
            ASPrivilege.str_to_enum("read_write_udf"), ASPrivilege.READ_WRITE_UDF
        )

    def test_is_global_only_scope(self):
        self.assertTrue(ASPrivilege.is_global_only_scope(ASPrivilege.DATA_ADMIN))
        self.assertTrue(ASPrivilege.is_global_only_scope(ASPrivilege.SYS_ADMIN))
        self.assertTrue(ASPrivilege.is_global_only_scope(ASPrivilege.USER_ADMIN))
        self.assertFalse(ASPrivilege.is_global_only_scope(ASPrivilege.READ))
        self.assertFalse(ASPrivilege.is_global_only_scope(ASPrivilege.READ_WRITE_UDF))
        self.assertFalse(ASPrivilege.is_global_only_scope(ASPrivilege.READ_WRITE))

    def test__str__(self):
        self.assertEqual(str(ASPrivilege.SYS_ADMIN), "sys-admin")
        self.assertEqual(str(ASPrivilege.DATA_ADMIN), "data-admin")
        self.assertEqual(str(ASPrivilege.USER_ADMIN), "user-admin")
        self.assertEqual(str(ASPrivilege.READ_WRITE_UDF), "read-write-udf")
        self.assertEqual(str(ASPrivilege.READ), "read")
        self.assertEqual(str(ASPrivilege.WRITE), "write")


class ASResponseTest(unittest.TestCase):
    def test__str__(self):
        self.assertEqual(str(ASResponse.UNKNOWN_SERVER_ERROR), "Unknown server error")
        self.assertEqual(
            str(ASResponse.NO_USER_OR_UNRECOGNIZED_USER), "No user or unrecognized user"
        )
        self.assertEqual(
            str(ASResponse.NO_CREDENTIAL_OR_BAD_CREDENTIAL),
            "No credential or bad credential",
        )
        self.assertEqual(str(ASResponse.NOT_WHITELISTED), "Not whitelisted")
        self.assertEqual(str(ASResponse.OK), "Ok")


"""
These tests were generated by capturing values send and received from the server.
Of course this only works it that units are written correctly and that might not
be the case.  Instead these are here to help reassure a developer that any
refactoring that they have made had not broken anything.
"""


class SecurityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.socket_mock = Mock()

    def test_login_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00[\x00\x00\x14\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00admin\x00\x00\x00=\x03$2a$10$7EqJtq98hPqEX7fNZaFWoO1mVO/4MLpGzsqojz6E9Gef6iXDjXdDa"
        self.socket_mock.recv.side_effect = [
            b"\x02\x02\x00\x00\x00\x00\x00R\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\x00\x00\x00>\x05B$2a$10$7EqJtq98hPqEX7fNZaFWoO1mVO/4MLpGzsqojz6E9Gef6iXDjXdDa",
        ]
        expected = (
            ASResponse.OK,
            b"B$2a$10$7EqJtq98hPqEX7fNZaFWoO1mVO/4MLpGzsqojz6E9Gef6iXDjXdDa",
            0,
        )

        actual = login(self.socket_mock, "admin", "admin", AuthMode.INTERNAL)

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertTupleEqual(actual, expected)

    def test_authenticate_new(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\\\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00admin\x00\x00\x00>\x05B$2a$10$7EqJtq98hPqEX7fNZaFWoO1mVO/4MLpGzsqojz6E9Gef6iXDjXdDa"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = authenticate_new(
            self.socket_mock,
            "admin",
            b"B$2a$10$7EqJtq98hPqEX7fNZaFWoO1mVO/4MLpGzsqojz6E9Gef6iXDjXdDa",
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_user_with_roles(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00p\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00bob\x00\x00\x00=\x01$2a$10$7EqJtq98hPqEX7fNZaFWoOv0hwU68nwGK8WvAqb5nnU0s/92caKv6\x00\x00\x00\x13\n\x02\nuser-admin\x05write"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = create_user(
            self.socket_mock, "bob", "pass", ["user-admin", "write"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_user_no_roles(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00`\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00nick\x00\x00\x00=\x01$2a$10$7EqJtq98hPqEX7fNZaFWoOv0hwU68nwGK8WvAqb5nnU0s/92caKv6\x00\x00\x00\x02\n\x00"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = create_user(self.socket_mock, "nick", "pass", [])

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_user_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, create_user, self.socket_mock, "nick", "pass", [])

    def test_drop_user_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x18\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00bob"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = drop_user(self.socket_mock, "bob")

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_drop_user_error(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x18\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00bob"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.NO_USER_OR_UNRECOGNIZED_USER

        actual_return_code = drop_user(self.socket_mock, "bob")

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_drop_user_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, drop_user, self.socket_mock, "nick")

    def test_set_password_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\\\x00\x00\x03\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00George\x00\x00\x00=\x01$2a$10$7EqJtq98hPqEX7fNZaFWoOo55z4.5EHedKkIBS22sgiJDvgvldAGm"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = set_password(self.socket_mock, "George", "a")

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_set_password_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, set_password, self.socket_mock, "bob", "a")

    def test_change_password_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x9d\x00\x00\x04\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00George\x00\x00\x00=\x02$2a$10$7EqJtq98hPqEX7fNZaFWoObi7T3EgttdiPRlkqhOALhpE/VOPU7Oi\x00\x00\x00=\x01$2a$10$7EqJtq98hPqEX7fNZaFWoOMUpJ9.8mF3fu.DNqcXCqdekYy8261c6"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = change_password(self.socket_mock, "George", "b", "z")

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_change_password_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, change_password, self.socket_mock, "bob", "a", "z")

    def test_grant_roles_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00<\x00\x00\x05\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00George\x00\x00\x00\x1d\n\x03\nuser-admin\tsys-admin\x05write"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = grant_roles(
            self.socket_mock, "George", ["user-admin", "sys-admin", "write"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_grant_roles_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError,
            grant_roles,
            self.socket_mock,
            "George",
            ["user-admin", "sys-admin", "write"],
        )

    def test_revoke_roles_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00<\x00\x00\x06\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00George\x00\x00\x00\x1d\n\x03\nuser-admin\tsys-admin\x05write"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = revoke_roles(
            self.socket_mock, "George", ["user-admin", "sys-admin", "write"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_revoke_roles_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError,
            revoke_roles,
            self.socket_mock,
            "George",
            ["user-admin", "sys-admin", "write"],
        )

    def test_query_users_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x10\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        self.socket_mock.recv.side_effect = [
            b"\x02\x02\x00\x00\x00\x00\x01\x10",
            b'\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00Bob-Ross\x00\x00\x00\x19\n\x03\x07Painter\x04read\tsys-admin\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00George\x00\x00\x00\r\n\x01\nnot-a-role\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00admin\x00\x00\x00"\n\x03\nread-write\tsys-admin\nuser-admin\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00d\x00\x00\x00\x02\n\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00nick\x00\x00\x00\x02\n\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00superwoman\x00\x00\x00\x0c\n\x01\tsys-admin',
            b"\x02\x02\x00\x00\x00\x00\x00\x10",
            b"\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ]
        expected_users = {
            "Bob-Ross": ["Painter", "read", "sys-admin"],
            "George": ["not-a-role"],
            "admin": ["read-write", "sys-admin", "user-admin"],
            "d": [],
            "nick": [],
            "superwoman": ["sys-admin"],
        }
        expected_return_code = ASResponse.OK

        actual_return_code, actual_users = query_users(self.socket_mock)

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)
        self.assertDictEqual(actual_users, expected_users)

    def test_query_users_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, query_users, self.socket_mock)

    def test_create_role_with_scoped_priv(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x002\x00\x00\n\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x10\x0c\x01\r\x04test\x07testset"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = create_role(
            self.socket_mock, "test-role", ["write.test.testset"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_role_with_scoped_priv_and_allowlist(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x006\x00\x00\n\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x0bb\x00\x00\x00\x10\x0c\x01\n\x04test\x07testset\x00\x00\x00\x08\r3.3.3.3"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = create_role(
            self.socket_mock, "b", ["read.test.testset"], ["3.3.3.3"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_role_with_scoped_priv(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x1f\x00\x00\n\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x0ba\x00\x00\x00\x05\x0c\x01\n\x00\x00"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = create_role(self.socket_mock, "a", ["read"])

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_role_error(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00'\x00\x00\n\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x05\x0c\x01\xff\x00\x00"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00G\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.ROLE_ALREADY_EXISTS

        actual_return_code = create_role(self.socket_mock, "test-role", ["not-priv"])

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_create_role_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError, create_role, self.socket_mock, "test-role", ["write.test.testset"]
        )

    def test_delete_role_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x1e\x00\x00\x0b\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = delete_role(self.socket_mock, "test-role")

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_delete_role_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, delete_role, self.socket_mock, "test-role")

    def test_add_privileges_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x002\x00\x00\x0c\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x10\x0c\x01\n\x04test\x07testset"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = add_privileges(
            self.socket_mock, "test-role", ["read.test.testset"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_add_privileges_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError, add_privileges, self.socket_mock, "test-role", "write"
        )

    def test_delete_privileges_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x002\x00\x00\r\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x10\x0c\x01\n\x04test\x07testset"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = delete_privileges(
            self.socket_mock, "test-role", ["read.test.testset"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_delete_privileges_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError, delete_privileges, self.socket_mock, "test-role", "write"
        )

    def test_delete_privileges_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x002\x00\x00\r\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x10\x0c\x01\n\x04test\x07testset"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = delete_privileges(
            self.socket_mock, "test-role", ["read.test.testset"]
        )

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_delete_privileges_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError, delete_privileges, self.socket_mock, "test-role", "write"
        )

    def test_set_whitelist(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00*\x00\x00\x0e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x08\r3.3.3.3"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = set_whitelist(self.socket_mock, "test-role", ["3.3.3.3"])

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_set_whitelist_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(
            IOError, set_whitelist, self.socket_mock, "test-role", ["3.3.3.3"]
        )

    def test_delete_whitelist(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x1e\x00\x00\x0e\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role"
        self.socket_mock.recv.return_value = b"\x02\x02\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        expected_return_code = ASResponse.OK

        actual_return_code = delete_whitelist(self.socket_mock, "test-role")

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)

    def test_query_roles_ok(self):
        expected_send_buf = b"\x00\x02\x00\x00\x00\x00\x00\x10\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        self.socket_mock.recv.side_effect = [
            b"\x02\x02\x00\x00\x00\x00\x01m",
            b"\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x0bPainter\x00\x00\x00\x08\r1.1.1.1\x00\x00\x00\x10\x0c\x01\r\x04test\x07testset\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x0bdata-admin\x00\x00\x00\x03\x0c\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x0bread\x00\x00\x00\x05\x0c\x01\n\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x0bread-write\x00\x00\x00\x05\x0c\x01\x0b\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x0bread-write-udf\x00\x00\x00\x05\x0c\x01\x0c\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0bsys-admin\x00\x00\x00\x03\x0c\x01\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x0btest-role\x00\x00\x00\x05\x0c\x01\r\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x0buser-admin\x00\x00\x00\x03\x0c\x01\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x0bwrite\x00\x00\x00\x05\x0c\x01\r\x00\x00",
            b"\x02\x02\x00\x00\x00\x00\x00\x10",
            b"\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ]
        expected_roles = {
            "Painter": {"privileges": ["write.test.testset"], "whitelist": ["1.1.1.1"]},
            "data-admin": {"privileges": ["data-admin"], "whitelist": []},
            "read": {"privileges": ["read"], "whitelist": []},
            "read-write": {"privileges": ["read-write"], "whitelist": []},
            "read-write-udf": {"privileges": ["read-write-udf"], "whitelist": []},
            "sys-admin": {"privileges": ["sys-admin"], "whitelist": []},
            "test-role": {"privileges": ["write"], "whitelist": []},
            "user-admin": {"privileges": ["user-admin"], "whitelist": []},
            "write": {"privileges": ["write"], "whitelist": []},
        }
        expected_return_code = ASResponse.OK

        actual_return_code, actual_roles = query_roles(self.socket_mock)

        self.socket_mock.sendall.assert_called_with(expected_send_buf)
        self.assertEqual(actual_return_code, expected_return_code)
        self.assertDictEqual(actual_roles, expected_roles)

    def test_query_roles_exception(self):
        self.socket_mock.sendall.side_effect = SocketError("message")

        self.assertRaises(IOError, query_roles, self.socket_mock)
