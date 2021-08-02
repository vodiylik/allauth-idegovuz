import setuptools

setuptools.setup(
     name='allauth-idegovuz',  
     version='0.1',
     author="Shukrullo Turgunov",
     author_email="sh@turgunov.uz",
     description="Allauth provider for id.egov.uz",
     url="https://code.track.uz/pythonistas/pip-packages/django-allauth-idegovuz",
     packages=setuptools.find_packages(),
     install_requires=['django', 'django-allauth'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
