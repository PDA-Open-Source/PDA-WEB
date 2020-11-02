# PDA [WebApp]

A Django(Python Web Framework) Application that allows user to create and conduct program.

The application has 5 personas :
* Super Administrator
* Entity Administrator
* Program Administrator
* Content Administrator
* Trainer

---
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
Things required to get the web application up and running.
* Python 3
* pip3
* Django 2.2.4
* PostgreSQL
* PyCharm CE 2019

### Installation
A step by step series of examples that tell you how to get a development environment running.

Run the below commands :-

# WebApp
* Open the Project Directory in PyCharm CE
* In Terminal > Goto Project Directory manage.py
* Create and Activate a Virtual Environment named .env
* Refer to the .example.env to configure the environment variables
* To Run Server :
```
    pip3 install -r requirements.txt
    python3 manage.py collectstatic
    python3 manage.py runserver <Port>
```

---
### Project Structure
```

+---PDA-WEB
    |   .env
    |   .example.env
    |   .gitignore
    |   manage.py
    |   README.md
    |   requirements.txt
    |   structure.txt
    |
    +---apps
    |   |   __init__.py
    |   |
    |   +---attestation
    |   |   |   admin.py
    |   |   |   apps.py
    |   |   |   models.py
    |   |   |   tests.py
    |   |   |   urls.py
    |   |   |   views.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---migrations
    |   |   |
    |   |   +---static
    |   |   |   \---css
    |   |   |           attestation-page.css
    |   |   |
    |   |   +---templates
    |   |   |   \---attestation
    |   |   |           trainer.html
    |   |   |
    |   |
    |   +---authentication
    |   |   |   admin.py
    |   |   |   apps.py
    |   |   |   middleware.py
    |   |   |   models.py
    |   |   |   tests.py
    |   |   |   urls.py
    |   |   |   views.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---migrations
    |   |   |
    |   |   +---static
    |   |   |   +---assets
    |   |   |   |
    |   |   |   +---css
    |   |   |   |       landing-page.css
    |   |   |   |       login.css
    |   |   |   |       signup-create-password.css
    |   |   |   |       signup-request-otp.css
    |   |   |   |       user-profile.css
    |   |   |   |
    |   |   |   \---js
    |   |   |       \---custom
    |   |   |               countryCodes.js
    |   |   |               encrypt.js
    |   |   |               mobileNumberValidation.js
    |   |   |               otp.js
    |   |   |
    |   |   +---templates
    |   |   |   \---authentication
    |   |   |           about-us.html
    |   |   |           forgot-password.html
    |   |   |           landing-page.html
    |   |   |           login.html
    |   |   |           privacy-policy.html
    |   |   |           reset-password.html
    |   |   |           signup-create-password.html
    |   |   |           signup-request-otp.html
    |   |   |           terms-and-conditions.html
    |   |   |           user-profile.html
    |   |   |
    |   |
    |   +---entity
    |   |   |   admin.py
    |   |   |   apps.py
    |   |   |   forms.py
    |   |   |   models.py
    |   |   |   tests.py
    |   |   |   urls.py
    |   |   |   views.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---migrations
    |   |   |
    |   |   +---static
    |   |   |   +---assets
    |   |   |   |
    |   |   |   +---css
    |   |   |   |   |   entity-list.css
    |   |   |   |   |   entity-profile.css
    |   |   |   |   |   entity-registration.css
    |   |   |   |
    |   |   |   |
    |   |   |   \---js
    |   |   |       \---custom
    |   |   |               entity.js
    |   |   |
    |   |   +---templates
    |   |   |   \---entity
    |   |   |           add-entity-admin-info.html
    |   |   |           add-entity-admin.html
    |   |   |           add-entity-info.html
    |   |   |           add-entity.html
    |   |   |           choose-scan-type.html
    |   |   |           edit_entity_profile.html
    |   |   |           entity-list.html
    |   |   |           entity_profile.html
    |   |   |           register-entity.html
    |   |   |
    |   |
    |   +---program
    |   |   |   admin.py
    |   |   |   apps.py
    |   |   |   forms.py
    |   |   |   models.py
    |   |   |   tests.py
    |   |   |   urls.py
    |   |   |   utils.py
    |   |   |   views.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---migrations
    |   |   |
    |   |   +---static
    |   |   |   |   custom.css
    |   |   |   |   entitylist.css
    |   |   |   |   form.css
    |   |   |   |   header.css
    |   |   |   |   participant-list.css
    |   |   |   |   tables.css
    |   |   |   |
    |   |   |   +---images
    |   |   |   |
    |   |   |   \---js
    |   |   |           plugin.js
    |   |   |
    |   |   +---templates
    |   |   |   |   layout.html
    |   |   |   |
    |   |   |   +---admin
    |   |   |   |       admin_program_detail.html
    |   |   |   |       admin_topic_detail.html
    |   |   |   |
    |   |   |   \---program
    |   |   |       +---detail
    |   |   |       |       add-admin-info.html
    |   |   |       |       add-admin.html
    |   |   |       |       index.html
    |   |   |       |       participant_list.html
    |   |   |       |       program_update.html
    |   |   |       |       topic-detail.html
    |   |   |       |       topic_create.html
    |   |   |       |       topic_update.html
    |   |   |       |       topic_update_1.html
    |   |   |       |
    |   |   |       +---list
    |   |   |       |       program_create.html
    |   |   |       |       program_list.html
    |   |   |       |
    |   |   |       \---session
    |   |   |               index.html
    |   |   |
    |   |   +---templatetags
    |   |   |   |   custom_tags.py
    |   |   |   |   __init__.py
    |   |   |
    |
    +---core
    |   |   apps.py
    |   |   models.py
    |   |   urls.py
    |   |   views.py
    |   |   __init__.py
    |   |
    |   +---migrations
    |   |   |   __init__.py
    |   |
    |   +---static
    |   |   +---assets
    |   |   |
    |   |   +---css
    |   |   |   \---custom
    |   |   |           base.css
    |   |   |           error.css
    |   |   |           fonts.css
    |   |   |           header.css
    |   |   |           in-body-qrscanner.css
    |   |   |           notification.css
    |   |   |           scanner.css
    |   |   |
    |   |   +---fonts
    |   |   |
    |   |   \---js
    |   |       \---custom
    |   |               notification.js
    |   |               scan.js
    |   |
    |   +---templates
    |   |   \---core
    |   |           base.html
    |   |           error.html
    |   |           header.html
    |   |           in-body-qrscanner.html
    |   |           notification.html
    |   |           partial-notification.html
    |   |           scanner.html
    |
    +---env
    |
    +---pda
    |   |   info_logs.py
    |   |   storage_backends.py
    |   |   urls.py
    |   |   wsgi.py
    |   |   __init__.py
    |   |
    |   +---settings
    |   |   |   base.py
    |   |   |   development.py
    |   |   |   production.py
    |   |   |   testing.py
    |   |   |   __init__.py

```
---
Please refer to [Wiki](https://github.com/PDA-Open-Source/PDA-WEB/wiki) for further details.
