(meeting-schedule)=

# Meeting schedule

We hold regular meetings, the timings of which are available on our [public calendar](https://calendar.google.com/calendar/embed?src=c_35r93ec6vtp8smhm7dv5uot0v4%40group.calendar.google.com).

If you are using napari or interested in how napari could be used in your work, please join one of our regular community meetings. If you're interested in diving deep on particular topic you could join the closest working group meeting. We currently have four working groups 'Bundled Application', 'Plugins', 'Architecture', and 'Documentation' that meet on a semi-regular candence. You can learn more about our working groups and community meetings in the corresponding discussion streams on the [napari Zulip](https://napari.zulipchat.com/login/).

<div id='community_calendar'></div>

<div id='timezone'></div>

<div id="eventDetailBackground" class="modal">
  <!-- Modal content -->
  <div class="modal-content">
    <div class="modal-header">
      <span class="close">&times;</span>
      <h3>Event details</h3>
    </div>
    <div id="details" class="modal-body">
    </div>
  </div>
</div>

<script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.9/index.global.min.js'></script>
<script src="https://cdn.jsdelivr.net/npm/@fullcalendar/google-calendar@6.1.9/index.global.min.js"></script>
<script>
  document.getElementById('timezone').innerHTML = "All times shown in "+Intl.DateTimeFormat().resolvedOptions().timeZone+".";
  document.addEventListener('DOMContentLoaded', function () {
    var community_calendar = document.getElementById('community_calendar');
    var calendar = new FullCalendar.Calendar(community_calendar,
    {
      height: 650,
      timeZone: 'local',
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,listWeek",
      },
      googleCalendarApiKey: '{API_KEY}',
      events: {
          googleCalendarId: 'c_35r93ec6vtp8smhm7dv5uot0v4@group.calendar.google.com',
      },
      eventDidMount: function (info) {
        if (info.event.title.toLowerCase().includes('community') || info.event.title.toLowerCase().includes('working')) {
          info.el.style.backgroundColor = 'var(--napari-primary-blue)';
          info.el.style.borderColor = 'var(--napari-primary-blue)';
        }
      },
      eventClick: function (info) {
        info.jsEvent.preventDefault();
        var eventObj = info.event;
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];
        // Get the modal
        var modal = document.getElementById("eventDetailBackground");
        modal.style.display = "block";
        var eventTitle = eventObj.title.charAt(0).toUpperCase() + eventObj.title.slice(1);
        var eventLocation = eventObj.extendedProps.location;
        document.getElementById("details").innerHTML = '<b>' + eventTitle + '</b>' + '<br>' + eventObj.extendedProps.description + '<br>' + '<b>Location: </b>' + '<a href='+eventLocation+'>'+eventLocation+'</a>';
        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
          modal.style.display = "none";
        }
        // When the user clicks anywhere outside of the modal, close it
        modal.onclick = function(event) {
          if (event.target.id == "eventDetailBackground") {
            modal.style.display = "none";
          }
        }
        window.addEventListener('keydown', function (event) {
          if (event.key === 'Escape') {
            modal.style.display = 'none'
          }
        })
      },
      eventDisplay: 'block',
    });
    calendar.render();
  });
</script>
