!(function ($) {
  "use strict";

  var CalendarApp = function () {
    this.$body = $("body");
    (this.$calendar = $("#calendar")),
      (this.$event = "#calendar-events div.calendar-events"),
      (this.$categoryForm = $("#add-new-event form")),
      (this.$extEvents = $("#calendar-events")),
      (this.$modal = $("#my-event")),
      (this.$saveCategoryBtn = $(".save-category")),
      (this.$calendarObj = null);
  };

  /* on drop */
  (CalendarApp.prototype.onDrop = function (eventObj, date) {
  
    var $this = this;
    // retrieve the dropped element's stored Event Object
    var originalEventObject = eventObj.data("eventObject");
    var $categoryClass = eventObj.attr("data-class");
    // we need to copy it, so that multiple events don't have a reference to the same object
    var copiedEventObject = $.extend({}, originalEventObject);
    // assign it the date that was reported
    copiedEventObject.start = date;
    if ($categoryClass) copiedEventObject["className"] = [$categoryClass];
    // render the event on the calendar
    $this.$calendar.fullCalendar("renderEvent", copiedEventObject, true);
    // is the "remove after drop" checkbox checked?
    if ($("#drop-remove").is(":checked")) {
      // if so, remove the element from the "Draggable Events" list
      eventObj.remove();
    }
  }),
    /* on click on event */
    (CalendarApp.prototype.onEventClick = function (calEvent, jsEvent, view) {
      // edit dan hapus agenda
      var $this = this;
      var form = $("<form action='' method=''></form>");
      form
      .append("<div class='row'></div>")
      .find(".row")
      .append(
        "<div class='col-md-12'><div class='form-group'><input class='form-control' placeholder='' value='"+
        calEvent.id + "' type='hidden' name='id'/></div></div>"
      )
      .append(
        "<div class='col-md-12'><div class='form-group'><label class='control-label'>Judul Agenda</label><input class='form-control' placeholder='Judul Agenda' value='"+
        calEvent.title + "' type='text' name='title'/></div></div>"
      )
      .append(
        "<div class='col-md-6'><div class='form-group'><label class='control-label'>Dari</label><input class='form-control' placeholder='Jam Mulai' value='"+
        calEvent.jam_mulai + "' type='datetime-local' name='start'/></div></div>"
      )
      .append(
        "<div class='col-md-6'><div class='form-group'><label class='control-label'>Sampai</label><input class='form-control' placeholder='Jam Selesai'value='"+
        calEvent.jam_selesai + "' type='datetime-local' name='end'/></div></div>"
      )
      .append(
        "<div class='col-md-12'><div class='form-group'><label class='control-label'>Pemimpin Kegiatan</label><input class='form-control' placeholder='ketua RT' value='"+
        calEvent.pemimpin_kegiatan + "' type='text' name='pemimpin_kegiatan'/></div></div>"
      )
      .append(
        "<div class='col-md-12'><div class='form-group'><label class='control-label'>Foto browsur <br><small>(*abaikan apabila tidak ada)</small></label><input class='form-control'value='"+
        calEvent.foto + "' type='file' name='foto'/></div></div>"
      )
      .append(
        "<div class='col-md-12'><div class='form-group'><label class='control-label'>Keterangan Kegiatan</label><textarea class='form-control' name='keterangan' rows='3' placeholder='Acara ini diadakan dalam rangka...'>"+
        calEvent.keterangan +"</textarea><small id='textHelp' class='form-text text-muted'></small></div></div>"
      );
      $this.$modal.show();
      $(".bckdrop").addClass("show");
      $(".bckdrop").removeClass("hide");
      $this.$modal
        .find(".delete-event")
        .show()
        .end()
        .find(".save-event")
        .hide()
        .end()
        .find(".modal-body")
        .empty()
        .prepend(form)
        .end()
        .find(".delete-event")
        .unbind("click")
        .click(function () {
          $this.$calendarObj.fullCalendar("removeEvents", function (ev) {
            return ev._id == calEvent._id;
          });
          $this.$modal.hide("hide");
          $(".bckdrop").addClass("hide");
          $(".bckdrop").removeClass("show");
              // Hapus agenda dengan Ajax
    $.ajax({
      type: 'DELETE',
      url: '/delete-agenda/'+calEvent.id,
      contentType: 'application/json',
      success: function (response) {
          console.log('Agenda deleted successfully:', response);
      },
      error: function (error) {
          console.error('Error deleting agenda:', error);
      }
  });
        });
      $this.$modal.find("form").on("submit", function () {
        console.log('submit');
        calEvent.title = form.find("input[name=title]").val();
        $this.$calendarObj.fullCalendar("updateEvent", calEvent);
        $this.$modal.hide("hide");
        $(".bckdrop").addClass("hide");
        $(".bckdrop").removeClass("show");

        return false;
      });
    }),
    /* on select */
    (CalendarApp.prototype.onSelect = function (start, end, allDay) {
      // tambah agenda
      var $this = this;
      $this.$modal.show();
      $(".bckdrop").addClass("show");
      $(".bckdrop").removeClass("hide");
      var form = $("<form action='/tambah-agenda' method='POST'></form>");
      form.append("<div class='row'></div>");
      form
        .find(".row")
        .append(
          "<div class='col-md-6'><div class='form-group'><label class='control-label'>Agenda Name</label><input class='form-control' placeholder='Insert Agenda Name' type='text' name='title'/></div></div>"
        )
        .append(
          "<div class='col-md-6'><div class='form-group'><label class='control-label'>Category</label><select class='form-select' name='category'></select></div></div>"
        )
        .append(
          "<div class='col-md-6'><div class='form-group'><label class='control-label'>Jam Mulai</label><input class='form-control' placeholder='Jam Mulai' type='datetime-local' name='start'/></div></div>"
        )
        .append(
          "<div class='col-md-6'><div class='form-group'><label class='control-label'>Jam Selesai</label><input class='form-control' placeholder='Jam Selesai' type='datetime-local' name='end'/></div></div>"
        )
        .append(
          "<div class='col-md-12'><div class='form-group'><label class='control-label'>Pemimpin Kegiatan</label><input class='form-control' placeholder='ketua RT'  type='text' name='pemimpin_kegiatan'/></div></div>"
        )
        .append(
          "<div class='col-md-12'><div class='form-group'><label class='control-label'>Foto browsur <br><small>(*abaikan apabila tidak ada)</small></label><input class='form-control' type='file' name='foto'/></div></div>"
        )
        .append(
          "<div class='col-md-12'><div class='form-group'><label class='control-label'>Keterangan Kegiatan</label><textarea class='form-control' name='keterangan' rows='3' placeholder='Acara ini diadakan dalam rangka...'></textarea><small id='textHelp' class='form-text text-muted'></small></div></div>"
        )
        .find("select[name='category']")
        .append(
          "<option value='bg-light-danger border-start border-2 border-danger'>Darurat</option>"
        )
        .append(
          "<option value='bg-light-success border-start border-2 border-success'>Event (lomba dsb)</option>"
        )
        .append(
          "<option value='bg-light-primary border-start border-2 border-primary'>Pemilihan</option>"
        )
        .append(
          "<option value='bg-warning border-start border-2 border-primary'>Penting</option>"
        )
        .append(
          "<option value='bg-light-warning border-start border-2 border-warning'>Pemberitahuan</option></div></div>"
        );
      $this.$modal
        .find(".delete-event")
        .hide()
        .end()
        .find(".save-event")
        .show()
        .end()
        .find(".modal-body")
        .empty()
        .prepend(form)
        .end()
        .find(".save-event")
        .unbind("click")
        .click(function () {
          form.submit();
          $(".bckdrop").addClass("hide");
          $(".bckdrop").removeClass("show");
          $("body").removeClass("modal-open");
        });
      $this.$modal.find(".close-dialog").click(function () {
        $this.$modal.hide("hide");
        $(".bckdrop").addClass("hide");
        $(".bckdrop").removeClass("show");
        $("body").removeClass("modal-open");
      });
      $("body").addClass("modal-open");
      $this.$modal.find("form").on("submit", function () {
        var title = form.find("input[name='title']").val();
        var beginning = form.find("input[name='beginning']").val();
        var ending = form.find("input[name='ending']").val();
        var categoryClass = form
          .find("select[name='category'] option:checked")
          .val();
        if (title !== null && title.length != 0) {
          $this.$calendarObj.fullCalendar(
            "renderEvent",
            {
              title: title,
              start: start,
              end: end,
              allDay: false,
              className: categoryClass,
            },
            true
          );
          $this.$modal.hide("hide");
          $(".bckdrop").addClass("hide");
          $(".bckdrop").removeClass("show");
        } else {
          alert("You have to give a title to your event");
        }
        return false;
      });
      $this.$calendarObj.fullCalendar("unselect");
    }),
    (CalendarApp.prototype.enableDrag = function () {
      //init events
      $(this.$event).each(function () {
        // create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
        // it doesn't need to have a start or end
        var eventObject = {
          title: $.trim($(this).text()), // use the element's text as the event title
        };
        // store the Event Object in the DOM element so we can get to it later
        $(this).data("eventObject", eventObject);
        // make the event draggable using jQuery UI
        $(this).draggable({
          zIndex: 999,
          revert: true, // will cause the event to go back to its
          revertDuration: 0, //  original position after the drag
        });
      });
    });
    function init_date(dateStringWithTime){

// Pisahkan tanggal, jam, dan menit dari string
var dateTimeParts = dateStringWithTime.split(', ');
var datePart = dateTimeParts[0];
var timePart = dateTimeParts[1];

var dateParts = datePart.split('/');
var day = parseInt(dateParts[0], 10);
var month = parseInt(dateParts[1], 10) - 1; // Bulan dimulai dari 0 (Januari = 0, Februari = 1, ...)
var year = parseInt(dateParts[2], 10);

var timeParts = timePart.split('.');
var hours = parseInt(timeParts[0], 10);
var minutes = parseInt(timeParts[1], 10);

// Membuat objek Date dengan tanggal, jam, dan menit yang ditentukan
var dateObject = new Date(year, month, day, hours, minutes);


return dateObject;
    }
    function init_datetime_local(dateStringWithTime){

      // Pisahkan tanggal, jam, dan menit dari string
      var dateTimeParts = dateStringWithTime.split(', ');
      var datePart = dateTimeParts[0];
      var timePart = dateTimeParts[1];
      
      var dateParts = datePart.split('/');
      var day = (parseInt(dateParts[0], 10) + 1).toString().padStart(2, '0');
      var month = (parseInt(dateParts[1], 10) + 1).toString().padStart(2, '0'); // Bulan dimulai dari 1 (Januari = 1, Februari = 2, ...)
      var year = parseInt(dateParts[2], 10);
      
      var timeParts = timePart.split('.');
      var hours =(parseInt(timeParts[0], 10) + 1).toString().padStart(2, '0');;
      var minutes = (parseInt(timeParts[1], 10) + 1).toString().padStart(2, '0');;
      
      // Membuat objek Date dengan tanggal, jam, dan menit yang ditentukan
      var dateObject = year+"-"+month+"-"+day+"T"+hours+":"+minutes;
      
      return dateObject;
          }
  /* Initializing */
  (CalendarApp.prototype.init = function () {
    // ambil db
    this.enableDrag();
    /*  Initialize the calendar  */
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
    var form = "";
    var today = new Date($.now());

    var DataDB = document.getElementById('data-container').getAttribute('data-db');
    DataDB = DataDB.replace(/'/g, '"')
    DataDB = DataDB.replace("'", '"')
    console.log(DataDB)
    var defaultEvents = [];
    var jsonData = JSON.parse(DataDB);
    for (var i = 0; i < jsonData.length; i++) {
      // Mengambil nilai id dan total dari setiap objek
      var title = jsonData[i].title;
      console.log(title)
      var start = jsonData[i].start;
      var end = jsonData[i].end;
      var kategori= jsonData[i].kategori;
      var className = '';
      if (kategori == 'darurat'){ 
        className = 'bg-light-danger border-start border-2 border-danger';
      }
      else if (kategori == 'penting'){ 
        className = 'bg-warning border-start border-2 border-warning';
      }
      else if (kategori == 'event'){ 
        className = 'bg-light-success border-start border-2 border-success';
      }
      else if (kategori == 'pemberitahuan'){ 
        className = 'bg-light-warning border-start border-2 border-warning';
      }
      else if (kategori == 'pemilihan'){ 
        className = 'bg-light-primary border-start border-2 border-primary';
      };

      let agenda = {
        title: title,
        start: init_date(start),
        end: init_date(end),
        jam_mulai: init_datetime_local(start),
        jam_selesai: init_datetime_local(end),
        className: className,
        id: jsonData[i].id,
        keterangan: jsonData[i].keterangan,
        foto:jsonData[i].foto,
        kategori:jsonData[i].kategori,
        pemimpin_kegiatan:jsonData[i].pemimpin_kegiatan
      }
      defaultEvents.push(agenda);

    }
    var $this = this;
    $this.$calendarObj = $this.$calendar.fullCalendar({
      slotDuration: "00:15:00",
      /* If we want to split day time each 15minutes */
      minTime: "08:00:00",
      maxTime: "19:00:00",
      defaultView: "month",
      handleWindowResize: true,

      header: {
        left: "prev,next today",
        center: "title",
        right: "month,agendaWeek",
      },
      events: defaultEvents,
      editable: true,
      droppable: false, // this allows things to be dropped onto the calendar !!!
      eventLimit: true, // allow "more" link when too many events
      selectable: true,
      drop: function (date) { // hapus event agenda
        $this.onDrop($(this), date);
    // delete  agenda
    console.log(date);
    $.ajax({
      type: "delete",
      url: "/delete-agenda", 
      contentType: "application/json",
      data: JSON.stringify(eventData),
      success: function(response) {
          console.log("Agenda deleted successfully:", response);
      },
      error: function(error) {
          console.error("Error saving event:", error);
      }});
      },
      select: function (start, end, allDay) { // edit event agenda
        $this.onSelect(start, end, allDay);

      },
      eventClick: function (calEvent, jsEvent, view) { //tambah event agenda
        $this.onEventClick(calEvent, jsEvent, view);

      },
    });

    //on new event
    this.$saveCategoryBtn.on("click", function () {
      var categoryName = $this.$categoryForm
        .find("input[name='category-name']")
        .val();
      var categoryColor = $this.$categoryForm
        .find("select[name='category-color']")
        .val();
      if (categoryName !== null && categoryName.length != 0) {
        $this.$extEvents.append(
          '<div class="calendar-events mb-3" data-class="bg-' +
            categoryColor +
            '" style="position: relative;"><i class="fa fa-circle text-' +
            categoryColor +
            ' me-2" ></i>' +
            categoryName +
            "</div>"
        );
        $this.enableDrag();
      }
    });
  }),
    //init CalendarApp
    ($.CalendarApp = new CalendarApp()),
    ($.CalendarApp.Constructor = CalendarApp);
})(window.jQuery),
  //initializing CalendarApp
  $(window).on("load", function () {
    $.CalendarApp.init();
  });
