from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Set up Arabic language support'

    def handle(self, *args, **options):
        self.stdout.write('🌍 Setting up Arabic language support...')
        
        # Create locale directory
        locale_dir = 'locale/ar/LC_MESSAGES'
        os.makedirs(locale_dir, exist_ok=True)
        
        # Create basic Arabic translations
        arabic_translations = {
            'admin': {
                'Users': 'المستخدمون',
                'Groups': 'المجموعات',
                'Add user': 'إضافة مستخدم',
                'Change user': 'تعديل مستخدم',
                'Delete user': 'حذف مستخدم',
                'Email': 'البريد الإلكتروني',
                'First name': 'الاسم الأول',
                'Last name': 'الاسم الأخير',
                'Phone number': 'رقم الهاتف',
                'Role': 'الدور',
                'Is verified': 'مُتحقق منه',
                'Is active': 'نشط',
                'Created at': 'تاريخ الإنشاء',
                'Updated at': 'تاريخ التحديث',
                'Last login': 'آخر تسجيل دخول',
                'Date joined': 'تاريخ الانضمام',
                'Personal info': 'المعلومات الشخصية',
                'Permissions': 'الصلاحيات',
                'Important dates': 'التواريخ المهمة',
            }
        }
        
        # Create a simple .po file
        po_content = '''msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Language: ar\\n"

msgid "Users"
msgstr "المستخدمون"

msgid "Groups"
msgstr "المجموعات"

msgid "Add user"
msgstr "إضافة مستخدم"

msgid "Change user"
msgstr "تعديل مستخدم"

msgid "Delete user"
msgstr "حذف مستخدم"

msgid "Email"
msgstr "البريد الإلكتروني"

msgid "First name"
msgstr "الاسم الأول"

msgid "Last name"
msgstr "الاسم الأخير"

msgid "Phone number"
msgstr "رقم الهاتف"

msgid "Role"
msgstr "الدور"

msgid "Is verified"
msgstr "مُتحقق منه"

msgid "Is active"
msgstr "نشط"

msgid "Created at"
msgstr "تاريخ الإنشاء"

msgid "Updated at"
msgstr "تاريخ التحديث"

msgid "Last login"
msgstr "آخر تسجيل دخول"

msgid "Date joined"
msgstr "تاريخ الانضمام"

msgid "Personal info"
msgstr "المعلومات الشخصية"

msgid "Permissions"
msgstr "الصلاحيات"

msgid "Important dates"
msgstr "التواريخ المهمة"
'''
        
        with open(f'{locale_dir}/django.po', 'w', encoding='utf-8') as f:
            f.write(po_content)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Arabic language support set up successfully!')
        )
        self.stdout.write('📝 You can now run: python manage.py compilemessages')
