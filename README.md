# ID.EGOV.UZ Provider for django-allauth

Author: Shukrullo Turgunov

## Install

- pip install idegovuz

## How to use?

- Add to installed apps list

```
  INSTALLED_APPS = [
        ...
        'idegovuz',
        ...
    ]

```

- Log in to Django administration page, in the Social Applications add new Social Application, enter your `client_id` and `client_secret`, in provider list select `id.egov.uz`, save it!
- That's it!
