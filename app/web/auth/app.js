var tg = window.Telegram.WebApp;

tg.MainButton.setText("Авторизоваться");
tg.MainButton.disable();
tg.MainButton.hide();

var html_form = document.getElementById("auth_config");
var base_url = window.location.origin + window.location.pathname;

var login_input = document.getElementById("login");
var password_input = document.getElementById("password");

login_input.addEventListener('input',function()
{
   maybe_allow_send();
})
password_input.addEventListener('input',function()
{
   maybe_allow_send();
})

function maybe_allow_send()
{
   if(login_input.value != '' && password_input.value != '')
   {
      tg.MainButton.enable();
      tg.MainButton.show();
   }
   else
   {
      tg.MainButton.disable();
      tg.MainButton.hide();
   }
}

Telegram.WebApp.onEvent('mainButtonClicked', function(){
   var formData = new FormData(html_form);
   var temp = {};
   var form = {
      'site': payload['site'],
      'user_id': payload['user_id'],
      'chat_id': payload['chat_id'],
      'message_id': payload['message_id'],
   };
   
   for(var pair of formData.entries())
   {
      temp[ pair[0] ] = pair[1];
   }

   if( 'login' in temp )
   {
      form['login'] = temp['login'];
   }

   if( 'password' in temp )
   {
      form['password'] = temp['password'];
   }


   const xhr = new XMLHttpRequest();
   xhr.open("POST", payload['host'] + "auth/setup");
   xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
   const body = JSON.stringify(form);
   xhr.onload = () => {
      if (xhr.readyState == 4 && xhr.status == 200) {
         console.log(JSON.parse(xhr.responseText));
         Telegram.WebApp.close();
      } else {
         alert(`Error: ${xhr.responseText}`);
         tg.MainButton.enable();
      }
   };
   xhr.send(body);
   tg.MainButton.disable();
});