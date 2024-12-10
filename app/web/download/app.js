var tg = window.Telegram.WebApp;

tg.MainButton.setText("Скачать");
tg.MainButton.enable();
tg.MainButton.show();

var html_form = document.getElementById("download_config");
var base_url = window.location.origin + window.location.pathname;

var start_input = document.getElementById("start");
var end_input = document.getElementById("end");
var images_checkbox = document.getElementById("images");
var format_select = document.getElementById("format");
format_select.addEventListener('change',function()
{
   maybe_toggle_fields();
})

function maybe_toggle_fields()
{
   if(start_input)
   {
      var start_input_row = start_input.closest('.form-row');
   }
   if(end_input)
   {
      var end_input_row = end_input.closest('.form-row');
   }
   if(images_checkbox)
   {
      var images_checkbox_row = images_checkbox.closest('.form-row');
   }
   if(format_select.value == 'mp3')
   {
      if(start_input_row)
      {
         start_input_row.classList.add('hidden');
      }
      if(end_input_row)
      {
         end_input_row.classList.add('hidden');
      }
      if(images_checkbox_row)
      {
         images_checkbox_row.classList.add('hidden');
      }
   }
   else
   {
      if(start_input_row)
      {
         start_input_row.classList.remove('hidden');
      }
      if(end_input_row)
      {
         end_input_row.classList.remove('hidden');
      }
      if(images_checkbox_row)
      {
         images_checkbox_row.classList.remove('hidden');
      }
   }
}

maybe_toggle_fields();

Telegram.WebApp.onEvent('mainButtonClicked', function(){
   var formData = new FormData(html_form);
   var temp = {};
   var form = {
      'link': payload['link'],
      'site': payload['site'],
      'user_id': payload['user_id'],
      'chat_id': payload['chat_id'],
      'message_id': payload['message_id'],
      'filename': payload['filename'],
   };
   
   for(var pair of formData.entries())
   {
      temp[ pair[0] ] = pair[1];
   }

   console.log(temp);

   if( 'start' in temp )
   {
      form['start'] = parseInt( temp['start'] );
   }

   if( 'end' in temp )
   {
      form['end'] = parseInt( temp['end'] );
   }

   if( 'format' in temp )
   {
      form['format'] = temp['format'];
   }

   if( 'auth' in temp )
   {
      form['auth'] = temp['auth'];
   }

   if( 'proxy' in temp )
   {
      form['proxy'] = temp['proxy'];
   }

   if( 'hashtags' in temp )
   {
      form['hashtags'] = temp['hashtags'];
   }

   if( 'images' in temp )
   {
      form['images'] = true;
   }

   if( 'cover' in temp )
   {
      form['cover'] = true;
   }

   if( 'force_images' in payload && payload['force_images'] )
   {
      form['images'] = true;
   }

   const xhr = new XMLHttpRequest();
   xhr.open("POST", payload['host'] + "download/setup");
   xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
   const body = JSON.stringify(form);
   xhr.onload = () => {
      if (xhr.readyState == 4 && xhr.status == 200) {
         console.log(JSON.parse(xhr.responseText));
         Telegram.WebApp.close();
      } else {
         alert(`Error: ${xhr.status}`);
         tg.MainButton.enable();
      }
   };
   xhr.send(body);
   tg.MainButton.disable();
});