import traceback

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import auth

# from demo.form import UserForm, ItemForm, ItemAddForm, UserAddForm, RoleForm, RoleAddForm, PermissionAddForm, \
#     RegisterForm
# from input.models import Role, User, UserRole, RolePermission, Item, Perm

from django.utils.functional import SimpleLazyObject

from demo.demo.form import UserForm, RegisterForm, ItemForm, ItemAddForm, UserAddForm, RoleForm, RoleAddForm
from demo.input.models import User, Item, Role, Perm, UserRole, RolePermission

class Login(View):
    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)  # POST请求提交表单，该视图将再次创建一个表单实例，数据绑定到表单，包含用户名和密码
        next_url = request.POST.get("next_url", None)
        if next_url == "None":
            next_url = None
        username = request.POST['username']
        password = request.POST['password']
        if form.is_valid():
            # 获取表单数据
            try:
                user_id = User.objects.get(username=username)
            except:
                return render(request, "login.html", {"username": username, "password": password, "error": "用户名错误"})
            user = authenticate(request, username=user_id, password=password)
            if user:
                auth.login(request, user)
                if next_url:
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect("/index/")
            else:
                return render(request, "login.html", {"username": username, "password": password, "error": "密码错误"})
        else:
            return render(request, "login.html", {"username": username, "password": password, "error": "登录失败"})

    def get(self, request, *args, **kwargs):
        next_url = request.GET.get("next", None)
        return render(request, "login.html", {"next_url": next_url})


class LogoutView(View):
    """
    用户登出
    """

    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect('/')


class Register(View):
    def post(self, request):
        form = RegisterForm(request.POST)  # 包含用户名和密码

        # 获取表单数据
        username = request.POST.get('username', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        data = {
            "username": username,
            "password1": password1,
            "password2": password2,
            "error": ""
        }
        if form.is_valid():
            # 添加到数据库
            user = User.objects.filter(username=username)
            if user:
                data["error"] = "用户名已存在"
                return render(request, "register.html", data)
            if password1 and password2:
                if password1 != password2:
                    data["error"] = "密码输入不一致，请重新输入密码"
                    return render(request, "register.html", data)
            try:
                User.objects.create_user(username=username, password=password1)
            except:
                data["error"] = "注册失败"
                return render(request, "register.html", data)
        else:
            data["error"] = "注册失败"
            return render(request, "register.html", data)
        return HttpResponseRedirect('/')

    def get(self, request, *args, **kwargs):
        return render(request, "register.html")


def index(request):
    return render(request, "index.html")


class ItemView(LoginRequiredMixin, View):
    """查看物料列表"""
    login_url = '/'
    # permission_required = 'view_item'

    def get(self, request, *args, **kwargs):
        context = []
        item = Item.objects.all().order_by('id')
        for i in item:
            data = {
                "id": i.id,
                "nr": i.nr,
                "name": i.name,
                "barcode": i.barcode,
            }
            context.append(data)
        return render(request, "item.html", {"data": context})


class ItemEdit(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "change_item"

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("change_item"):
            item_id = request.GET.get('item_id', None)
            try:
                item = Item.objects.get(id=item_id)
                data = {
                    "id": item.id,
                    "nr": item.nr,
                    "name": item.name,
                    "barcode": item.barcode,
                }
            except:
                return HttpResponseRedirect("/item/?msg=数据查询失败")

        else:
            return HttpResponseRedirect("/item/?msg=用户没有编辑物料的权限")

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("change_item"):
            form = ItemForm(request.POST)
            # 获取表单数据
            item_id = request.POST['id']
            nr = request.POST['nr']
            name = request.POST['name']
            barcode = request.POST['barcode']
            data = {
                "id": item_id,
                "nr": nr,
                "name": name,
                "barcode": barcode,

            }
            if form.is_valid():

                with transaction.atomic(savepoint=False):
                    # 创建保存点
                    try:
                        item = Item.objects.get(id=item_id)
                        item.nr = nr
                        item.name = name
                        item.barcode = barcode
                        item.save()
                    except:
                        return render(request, "item_edit.html", {"data": data, "error": "编辑失败"})
                    else:
                        return HttpResponseRedirect("/item/")
            else:
                return render(request, "item_edit.html", {"data": data, "error": "表单填写错误"})

        else:
            return HttpResponseRedirect("/item/?msg=用户没有编辑物料的权限")



class ItemDelete(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "delete_item"

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("delete_item"):
            item_id = request.GET.get('item_id', None)
            try:
                item = Item.objects.first(id=item_id)
                data = {
                    "id": item.id,
                    "nr": item.nr,
                    "name": item.name,
                    "barcode": item.barcode,
                }
            except Exception as e:
                traceback.print_exc()
                return HttpResponseRedirect("/item/?msg=数据查询失败")

            return render(request, "item_delete.html", {"data": data})
        else:
            return HttpResponseRedirect("/item/?msg=用户没有权限")

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("delete_item"):
            item_id = request.GET.get('item_id', None)
            with transaction.atomic(savepoint=False):
                # 创建保存点
                try:
                    item = Item.objects.get(id=item_id)
                    item.delete()
                except:
                    return HttpResponseRedirect("/item_delete/?msg=删除失败")
                else:
                    return HttpResponseRedirect('/item/')

        else:
            return HttpResponseRedirect("/item/?msg=用户没有权限")


class ItemAdd(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "add_item"

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("add_item"):
            return render(request, "item_add.html")
        else:
            return HttpResponseRedirect("/item/?msg=用户没有权限")

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("add_item"):
            form = ItemAddForm(request.POST)
            # 获取表单数据
            nr = request.POST['nr']
            name = request.POST['name']
            barcode = request.POST['barcode']
            data = {
                "nr": nr,
                "name": name,
                "barcode": barcode
            }
            if form.is_valid():

                with transaction.atomic(savepoint=False):
                    try:
                        Item.objects.create(nr=nr, name=name, barcode=barcode)
                    except:
                        return render(request, "item_add.html", {"data": data, "error": "添加失败，物料代码已存在"})
                    else:
                        return HttpResponseRedirect("/item/")
            else:
                return render(request, "item_edit.html", {"data": data, "error": "表单错误"})
        else:

            return HttpResponseRedirect("/item/?msg=用户没有权限")

class UserView(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "view_user"

    def get(self, request, *args, **kwargs):
        """获取用户列表"""
        if request.user.has_perm("view_user"):

            content = {
                "error": "",
                "data": []

            }
            user = User.objects.all().order_by('id')
            for i in user:
                data = {
                    "id": i.id,
                    "username": i.username,
                    "is_superuser": i.is_superuser,
                }
                content["data"].append(data)
            return render(request, "user.html", content)
        else:
            return HttpResponseRedirect("/item/?msg=用户没有权限")


class UserEdit(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "change_user"

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("change_user"):

            user_id = request.GET.get('user_id', None)
            try:
                user = User.objects.get(id=user_id)
                data = {
                    "id": user.id,
                    "username": user.username,
                    "is_superuser": user.is_superuser,
                }
            except:
                return HttpResponseRedirect("/user/?msg=数据查询失败")

            return render(request, "user_edit.html", {"data": data})
        else:
            return HttpResponseRedirect("/item/?msg=用户没有权限")

    def post(self, request, *args, **kwargs):
        form = UserAddForm(request.POST)
        if request.user.has_perm("change_user"):

            if form.is_valid():
                # 获取表单数据
                user_id = form.cleaned_data['id']
                username = form.cleaned_data['username']
                is_superuser = form.cleaned_data['is_superuser']
                with transaction.atomic(savepoint=False):
                    # 创建保存点
                    try:
                        user = User.objects.get(id=user_id)
                        user.username = username
                        user.is_superuser = is_superuser
                        user.save()
                    except:
                        return render(request, "user_edit.html", {"error": "编辑失败"})
                    else:
                        return HttpResponseRedirect("/user/")
            else:
                return render(request, "user_edit.html", {"error": "表单填写错误"})
        else:
            return HttpResponseRedirect("/item/?msg=用户没有权限")


class UserDelete(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required="delete_user"

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', None)
        try:
            user = User.objects.get(id=user_id)
            data = {
                "id": user.id,
                "username": user.username,
                "is_superuser": user.is_superuser,
            }
        except:
            return HttpResponseRedirect("/user/?msg=数据查询失败")

        return render(request, "user_delete.html", {"data": data})

    def post(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', None)
        with transaction.atomic(savepoint=False):
            # 创建保存点
            try:
                user = User.objects.get(id=user_id)
                user.delete()
            except Exception as e:
                print(e)
                return HttpResponseRedirect("/user_delete/?msg=删除失败")

            else:
                return HttpResponseRedirect('/user/')


class RoleView(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required="view_role"

    def get(self, request, *args, **kwargs):
        """获取用户列表"""

        content = {
            "error": "",
            "data": []

        }
        role = Role.objects.all().order_by('id')
        for i in role:
            data = {
                "id": i.id,
                "name": i.name,
            }
            content["data"].append(data)
        return render(request, "role.html", content)


class RoleEdit(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "change_role"

    def get(self, request, *args, **kwargs):

        role_id = request.GET.get('role_id', None)
        try:
            role = Role.objects.get(id=role_id)
            data = {
                "id": role.id,
                "name": role.name,
            }
        except:
            return HttpResponseRedirect("/role/?msg=查询角色信息失败")

        return render(request, "role_edit.html", {"message": "物料数据返回成功", "data": data})

    def post(self, request, *args, **kwargs):
        form = RoleForm(request.POST)
        role_id = request.POST['id']
        name = request.POST['name']
        data = {
            "id": role_id,
            "name": name
        }
        if form.is_valid():
            # 获取表单数据
            with transaction.atomic(savepoint=False):
                # 创建保存点
                try:
                    role = Role.objects.get(id=role_id)
                    role.name = name
                    role.save()
                except:

                    return render(request, "role_edit.html", {"data": data, "error": "编辑失败"})
                else:
                    return HttpResponseRedirect("/role/")
        else:
            return render(request, "role_edit.html", {"data": data, "error": "表单填写错误"})


class RoleAdd(LoginRequiredMixin, View):
    login_url = '/'
    # permission_required = "add_role"

    def get(self, request, *args, **kwargs):

        if request.user.has_perm("add_role"):
            return render(request, "role_add.html")
        else:
            return HttpResponseRedirect("/role/?msg=用户没有添加角色的权限")

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("add_role"):
            form = RoleAddForm(request.POST)
            name = request.POST['name']
            data = {
                "name": name
            }

            if form.is_valid():
                # 获取表单数据
                with transaction.atomic(savepoint=False):
                    try:
                        Role.objects.create(name=name)
                    except Exception as e:
                        print(e)
                        return render(request, "role_add.html", {"data": data, "error": "添加失败,角色名称已存在"})
                    else:
                        return HttpResponseRedirect("/role/")
            else:
                return render(request, "role_add.html", {"data": data, "error": "表单错误"})
        else:
            return HttpResponseRedirect("/role/?msg=用户没有添加角色的权限")


class RoleDelete(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):

        if request.user.has_perm("delete_role"):
            role_id = request.GET.get('role_id', None)
            try:
                role = Role.objects.get(id=role_id)
                data = {
                    "id": role.id,
                    "name": role.name,
                }
            except:
                return HttpResponseRedirect("/role/?msg=数据查询失败")

        else:
            return HttpResponseRedirect("/role/?msg=用户没有删除角色的权限")

        return render(request, "role_delete.html", {"message": "数据返回成功", "data": data})

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("delete_role"):
            role_id = request.GET.get('role_id', None)

            with transaction.atomic(savepoint=False):
                # 创建保存点
                try:
                    role = Role.objects.get(id=role_id)
                    role.delete()
                except Exception as e:
                    print(e)
                    return HttpResponseRedirect("/role_delete/?msg=删除失败")
                else:
                    return HttpResponseRedirect('/role/')
        else:
            return HttpResponseRedirect("/role/?msg=用户没有删除角色的权限")


class PermissionView(LoginRequiredMixin, View):
    login_url = '/'
    """权限"""

    def get(self, request, *args, **kwargs):
        content = {
            "message": "",
            "data": []
        }

        if request.user.has_perm("view_perm"):
            perms = Perm.objects.all()
            for i in perms:
                data = {
                    "id": i.id,
                    "name": i.name,
                    "codename": i.codename
                }
                content["data"].append(data)
        else:
            return HttpResponseRedirect("/index/?msg=用户没有查看权限信息的权限")

        return render(request, "permission.html", content)


class UserRoleView(LoginRequiredMixin, View):
    """用户角色"""
    login_url = '/'

    def get(self, request, *args, **kwargs):
        content = {
            "error": "",
            "data": [],
            "all_role_dict": []

        }
        if request.user.has_perm("view_user_role"):
            user_role_list = []
            users = User.objects.all().order_by('id')
            all_roles = Role.objects.all().values("id", "name").order_by('id')
            all_role_dict = {}
            for i in list(all_roles):
                all_role_dict[i["id"]] = i["name"]

            for user in users:
                roles = UserRole.objects.filter(user=user).values("role__name").order_by('id')
                roles_list = [i["role__name"] for i in list(roles)]
                user_role = {
                    "id": user.id,
                    "user": user.username,
                    "role": roles_list,
                }
                user_role_list.append(user_role)
            content["data"] = user_role_list
            content["all_role_dict"] = all_role_dict

            return render(request, "user_role.html", content)
        else:
            return HttpResponseRedirect("/index/?msg=用户没有查看用户角色的权限")


class UserRoleEdit(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("chenge_user_role"):
            user_id = request.GET.get("user_id", None)
            try:
                user = User.objects.get(id=user_id)
            except:
                return HttpResponseRedirect("/user_role/?msg=没有找到数据")
            roles = UserRole.objects.filter(user=user).values("role__name").order_by('id')
            all_roles = Role.objects.all().values("id", "name").order_by('id')
            all_role_dict = {}
            for i in list(all_roles):
                all_role_dict[i["id"]] = i["name"]

            roles_list = [i["role__name"] for i in list(roles)]
            user_role = {
                "id": user_id,
                "user": user.username,
                "roles_list": roles_list,
                "all_role_dict": all_role_dict
            }
            return render(request, "user_role_edit.html", user_role)
        else:
            return HttpResponseRedirect("/user_role/?msg=用户没有编辑用户角色的权限")

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("change_user_role"):
            user_id = request.POST["id"]
            roles = request.POST['roles_arr']
            role_list = roles.split(',')
            if roles:

                role_int_list = list(map(lambda x: int(x), list(filter(lambda x: type(x) is str, role_list))))
            else:
                role_int_list = []
            with transaction.atomic(savepoint=False):
                try:
                    user = User.objects.get(id=user_id)
                    UserRole.objects.filter(user=user).delete()
                    if role_int_list:
                        for i in role_int_list:
                            role = Role.objects.get(id=i)
                            UserRole.objects.create(user=user, role=role)
                except Exception as e:
                    print(e)
                    return HttpResponseRedirect("/user_role/edit/?msg=编辑用户角色信息失败")

                return HttpResponseRedirect("/user_role/")

        else:
            return HttpResponseRedirect("/index/?msg=用户没有编辑用户角色的权限")


class RolePermissionView(LoginRequiredMixin, View):
    """角色权限"""
    login_url = '/'

    def get(self, request, *args, **kwargs):
        content = {
            "error": "",
            "data": [],
            "all_perm_dict": {}

        }
        if request.user.has_perm("view_role_permission"):
            role_perm_list = []
            roles = list(Role.objects.all().order_by('id'))
            all_perms = list(Perm.objects.all().values("id", "codename").order_by('id'))
            all_perm_dict = {}
            for i in all_perms:
                all_perm_dict[i["id"]] = i["codename"]

            # for role in roles:
            #     perms = RolePermission.objects.filter(role=role).values("permission__codename").order_by('id')
            #     perms_list = [i["permission__codename"] for i in list(perms)]
            #     user_role = {
            #         "id": role.id,
            #         "role": role.name,
            #         "perm": perms_list,
            #     }

            perms = list(RolePermission.objects.filter(role_id__in=[i.id for i in roles]))
            for role in roles:
                perms_ids = list(map(lambda x: x.permission_id, filter(lambda i: i.role_id == role.id, perms)))
                perms_list = list(
                    map(lambda x: x['codename'], filter(lambda i: perms_ids.__contains__(i["id"]), all_perms)))
                user_role = {
                    "id": role.id,
                    "role": role.name,
                    "perm": perms_list,
                }
                role_perm_list.append(user_role)

            #
            content["data"] = role_perm_list
            content["all_perm_dict"] = all_perm_dict
            return render(request, "role_permission.html", content)

        else:
            return HttpResponseRedirect("/index/?msg=用户没有查看角色权限信息的权限")


class RolePermissionEdit(LoginRequiredMixin, View):
    """角色权限"""
    login_url = '/'

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("change_role_permission"):
            role_id = request.GET.get("role_id", None)
            try:
                role = Role.objects.get(id=role_id)
            except:
                return HttpResponseRedirect("/role_permission/?msg=没有找到数据")
            perms = RolePermission.objects.filter(role=role).values("permission__codename").order_by('id')
            perms_list = [i["permission__codename"] for i in list(perms)]
            all_perm = Perm.objects.all().values("id", "codename").order_by('id')
            all_perm_dict = {}
            for i in list(all_perm):
                all_perm_dict[i["id"]] = i["codename"]

            role_perm = {
                "id": role.id,
                "role": role.name,
                "perms_list": perms_list,
                "all_perm_dict": all_perm_dict
            }

            return render(request, "role_permission_edit.html", role_perm)
        else:
            return HttpResponseRedirect("/role_permission/?msg=用户没有编辑角色权限信息的权限")

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("change_role_permission"):
            role_id = request.POST["id"]
            permissions = request.POST['perms_arr']
            perm_list = permissions.split(',')
            # 判断权限是列表是否为空
            perm_int_list = set(
                map(lambda x: int(x), list(filter(lambda x: type(x) is str, perm_list)))) if permissions else set()

            with transaction.atomic(savepoint=False):
                try:
                    pids = set(RolePermission.objects.filter(role_id=role_id).values_list('permission_id', flat=True))
                    # 删除被取消的权限
                    delete_ids = pids.difference(perm_int_list)
                    # 创建新添加的权限
                    add_ids = perm_int_list.difference(pids)

                    RolePermission.objects.filter(role_id=role_id, permission_id__in=delete_ids).delete()
                    RolePermission.objects.bulk_create(
                        [RolePermission(role_id=role_id, permission_id=pid) for pid in add_ids])
                except:
                    return HttpResponseRedirect("/role_permission/edit/?msg=修改角色权限信息失败")
                return HttpResponseRedirect("/role_permission/")
        else:
            return HttpResponseRedirect("/role_permission/?msg=用户没有查看角色权限信息的权限")
