"""
@author :  Ashish joshi , Vatsal patel, Nao Itoi , Tilak Shenoy
"""
from pywinauto.application import Application
from pywinauto import Desktop
import time 
import sys,subprocess
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time

def goTonext(dialog,repeat=1):
    for i in range(repeat):
        dialog.next.wait('enabled',timeout=100).click()
    
def clickInstall(dialog):
    dialog.install.wait('enabled',timeout=100).click()

def inputApplicationDetails(dialog,clientid=" ",secret=" ",orgurl=" "):
    dialog.Edit.type_keys(clientid)
    dialog.Edit2.type_keys(secret)
    dialog.Edit3.type_keys(orgurl)

def waitForFinish(dialog):
    while dialog.cancel.is_enabled():
        pass
    dialog.Close.click()
    
def activateMFAPlugin(name):
    #Enabling the ADFS plugin 
    cmd = "Set-AdfsGlobalAuthenticationPolicy –AdditionalAuthenticationProvider "+name
    subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    
def mfa_End_Auth():
    driver = webdriver.Chrome(executable_path=r"C:\Users\Administrator\Downloads\chromedriver_win32\chromedriver.exe")
    driver.get("https://ec2amaz-q599aig.testad.com/adfs/ls/IdpInitiatedSignOn.aspx")
    driver.find_element("id","idp_SignInButton").click()
    driver.find_element("id","userNameInput").send_keys("ahassan@testad.com")
    driver.find_element("id","passwordInput").send_keys("Abcd1234")
    driver.find_element("id","submitButton").click()

    time.sleep(6)
    actions = ActionChains(driver)
    actions.send_keys('okta\n')
    actions.perform()

    element = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "idp_SignOutButton")) 
    driver.find_element("id","idp_SignOutButton").click()
    driver.close()
    
    
def embeddedBrowserLogin(username,password):
    d = Desktop(backend='uia')
    main_window = d.window(title_re='Sign into Okta with Administrative User Account', control_type="Window")
    main_window.wait('visible')
    main_window.edit.set_edit_text(u'')
    main_window.edit.type_keys(username)
    main_window.next.click()
    time.sleep(2)
    main_window.edit.set_edit_text(u'')
    main_window.edit.type_keys(password)
    time.sleep(2)
    main_window.verify.click()
    time.sleep(2)
    main_window.AllowAccess.click()
    
def radiusAuth(username,password,otp):
    import subprocess
    Auth="java -jar C:\\jradius-client\\target\\jradius.jar -r 10.20.193.133:2002 -s "+password+" -u " +username+" -p "+password+" -a "+otp
    print(Auth)
    p=subprocess.Popen(Auth, stdout=subprocess.PIPE, shell=True)

    (output, err) = p.communicate()
     
    ## Wait for date to terminate. Get return returncode ##
    p_status = p.wait()
    print ("Command output : ", output)
    print ("Command exit status/return code : ", p_status)

    Auth_Sucess="Reply-Message = Welcome radius_sq@oktatest.com!"

    if Auth_Sucess in str(output):
        print("Auth Success")
    else:
        print("Auth Failure")
    
  

if sys.argv[1].lower() == "adfs":
    
    #installing the agent 
    commands=r"msiexec /i C:\Users\Administrator\Downloads\OktaADFSAdapter-1.7.11.0-be62f37\OktaMFAProvider.msi"
    app = Application(backend="uia").start(commands)
    main_dlg = app.OktaMFAProvider
    goTonext(main_dlg)
    inputApplicationDetails(main_dlg,"0oa48ywdl2PKEEsuz0g7","ubOP-NlwfuTWLP_TI4HR_OFuV_4ScCkilN-PtOPk","https://aj-tc1-oie.trexcloud.com")
    goTonext(main_dlg)
    main_dlg.checkbox.click()
    goTonext(main_dlg,4)
    waitForFinish(main_dlg)
    
    #Activate MFA Plugin
    activateMFAPlugin("OktaMfaAdfs")
    
    #Authentication
    mfa_End_Auth()
    
      
elif sys.argv[1].lower() == "radius":
    app = Application(backend="uia").start(r"C:\Users\Administrator\Desktop\Radius-fips\OktaRadiusAgentSetup-2.18.0-9866f6f.exe")
    main_dlg = app.OktanRadiusAgent
    main_dlg.wait('visible')
    goTonext(main_dlg,3)
    clickInstall(main_dlg)
    while not main_dlg.next.is_enabled():
        pass
    goTonext(main_dlg)
    main_dlg.edit.type_keys("https://qa-mfaaaservice-oie-tc1.trexcloud.com")
    goTonext(main_dlg)

    #Embedded Browser section starts#
    embeddedBrowserLogin("abir.hassan","Abcd1234")
    #Embedded Browser section ends#
    
    main_dlg.finish.wait('enabled',timeout=200).click()
    
    #Authentication
    radiusAuth("radius_sq@oktatest.com","Abcd1234","oktapus")



    
    






