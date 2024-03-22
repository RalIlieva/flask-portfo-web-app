//     function initialize_popovers() {
//        const popups = document.getElementsByClassName('user_popup');
//        for (let i = 0; i < popups.length; i++) {
//          const popover = new bootstrap.Popover(popups[i], {
//            content: 'Loading...',
//            trigger: 'hover focus',
//            placement: 'right',
//            html: true,
//            sanitize: false,
//            delay: {show: 500, hide: 0},
//            container: popups[i],
//            customClass: 'd-inline',
//          });
//          popups[i].addEventListener('show.bs.popover', async (ev) => {
//            if (ev.target.popupLoaded) {
//              return;
//            }
//            const response = await fetch('/profile/' + ev.target.innerText.trim() + '/popup');
//            const data = await response.text();
//            const popover = bootstrap.Popover.getInstance(ev.target);
//            if (popover && data) {
//              ev.target.popupLoaded = true;
//              popover.setContent({'.popover-body': data});
//              flask_moment_render_all();
//            }
//          });
//        }
//      }
//      document.addEventListener('DOMContentLoaded', initialize_popovers);
//
//       function set_message_count(n) {
//        const count = document.getElementById('message_count');
//        count.innerText = n;
//        count.style.visibility = n ? 'visible' : 'hidden';
//      }
//
//     {% if current_user.is_authenticated %}
//      function initialize_notifications() {
//        let since = 0;
//        setInterval(async function() {
//          const response = await fetch('{{ url_for('views.notifications') }}?since=' + since);
//          const notifications = await response.json();
//          for (let i = 0; i < notifications.length; i++) {
//            if (notifications[i].name == 'unread_message_count')
//              set_message_count(notifications[i].data);
//            since = notifications[i].timestamp;
//          }
//        }, 10000);
//      }
//      document.addEventListener('DOMContentLoaded', initialize_notifications);
//      {% endif %}
