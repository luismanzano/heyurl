import random
import string

from django.shortcuts import render
from django.http import HttpResponse
from .models import Url, Click
from .helpers import validate_url
from django.shortcuts import redirect
from datetime import datetime
from .forms import CreateNewShortUrl

def index(request):
    urls = Url.objects.order_by('-created_at')
    context = {'urls': urls}
    return render(request, 'heyurl/index.html', context)


def data_panel(request, url):
    today = datetime.now()
    ident = Url.objects.filter(short_url=url)
    ident = ident[0].id

    # GETTING THE CLICKS THIS MONTH
    clicks_this_month = Click.objects.filter(url=ident, created_at__year=today.year,
                                             created_at__month=today.month)

    # TOTAL CLICKS PER BROWSER
    safari = Click.objects.filter(url=ident, browser__contains='safari')
    chrome = Click.objects.filter(url=ident, browser__contains='chrome')
    firefox = Click.objects.filter(url=ident, browser__contains='firefox')

    # TOTAL CLICKS PER PLATFORM
    mobile = Click.objects.filter(url=ident, platform='Mobile')
    pc = Click.objects.filter(url=ident, platform='PC')

    #CONTEXT TO DISPLAY ON DATA PANEL
    context = {
        'url': url,
        'clicks': len(clicks_this_month),
        'safari': len(safari),
        'chrome': len(chrome),
        'firefox': len(firefox),
        'mobile': len(mobile),
        'pc': len(pc),
    }

    return render(request, 'heyurl/data_panel.html', context)


def store(request):
    # RECEIVING AND VALIDATING THE REQUEST
    if request.method == 'POST':
        form = CreateNewShortUrl(request.POST)
    print("POST", request.POST["original_url"])
    # CHECK IF THE URL IS VALID
    if validate_url(request.POST['original_url']) == False:
        return HttpResponse("The provided url does not exist, please try with a different one :)")

    # CHECK IF THERE IS ALREADY A SHORT FOR SUBMITTED URL
    if Url.objects.filter(original_url=request.POST['original_url']):
        return HttpResponse("There is already a shortened version of this url, please try with a new one")

    if form.is_valid():
        original_website = form.cleaned_data['original_url']
        random_chars_list = list(string.ascii_letters)
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        random_chars_list += numbers

        new_short_url = ''
        for i in range(5):
            new_short_url += random.choice(random_chars_list)

        new_date = datetime.now()
        new_url = Url(original_url=original_website, short_url=new_short_url,
                      clicks=0, created_at=new_date, updated_at=new_date)
        new_url.save()

        form = CreateNewShortUrl()
        return HttpResponse("Storing a new URL object into storage")

def short_url(request, url):
    current_obj = Url.objects.filter(short_url=url)

    # LETS CREATE THE DATE WHERE THE CLICKS IS CREATED
    now_date = datetime.now()
    # GET THE DEVICE WHERE THE CLICK IS BEING CALLED
    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        device = "Mobile"
    else:
        device = "PC"
    # GET THE BROWSER
    browser = str(request.user_agent.browser.family)

    # SAVING THE CLICK
    new_click = Click(url=current_obj[0], created_at=now_date, updated_at=now_date, platform=device, browser=browser)
    new_click.save()
    # UPDATING THE CLICK COUNT ON THE URL OBJECT
    Url.objects.filter(short_url=url).update(clicks=current_obj[0].clicks + 1)

    # CHECKING THAT IS IS A VALID URL
    if not validate_url(current_obj[0].original_url):
        return render(request, 'heyurl/404.html')
    # WHEN USER CLICKS AUTOMATICALLY GETS REDIRECTED TO WHERE THEY INTENDED TO GO
    return redirect(current_obj[0].original_url)
