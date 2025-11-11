$(document).keyup(function(e) {
  if (e.keyCode == 27) {
    //escape key
    window.location.reload();
  }
});

var globalTimeout = null;

if (globalTimeout != null) {
  clearTimeout(globalTimeout);
}

//
// ATTEMPT
//

attemptViewForm = function(id) {
  $("#value_attempt_" + id).hide();
  $("#validate_" + id).hide();
  $("#form_attempt_" + id).show();
  $("#input_attempt_" + id).select();
  $("#input_attempt_" + id).keypress(function(event) {
    var keycode = event.keyCode ? event.keyCode : event.which;
    if (keycode == "13") {
      attemptSaveValue(id);
    }
  });
};

attemptSaveValue = function(id) {
  value = $("#input_attempt_" + id).val();
  if (!value) {
    value = "0";
  }
  var request = $.ajax({
    url: "/scoresheet/attempt/change/" + value + "/" + id,
    type: "get",
    cache: false,
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });

  request.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
  });
};

//
// CONCURRENT
//

$("#concurrentGet").on("keyup", function(event) {
  event.preventDefault();
  if (globalTimeout != null) {
    clearTimeout(globalTimeout);
  }

  if (event.which == 27) {
    $("#concurrentGetResultList").hide();
    exit;
  }

  var motif = this.value;
  if (this.value.length < 2) {
    $("#concurrentGetResultList").hide();
    $("#concurrentSelect")
      .children()
      .remove();
    return;
  }

  currentCompetition = $("#currentCompetiton").val();
  gender = $("#gender_id").val();
  globalTimeout = setTimeout(function() {
    globalTimeout = null;
    var request = $.ajax({
      url:
        "/scoresheet/concurrent/get/" +
        $("#concurrentGet").val() +
        "/" +
        currentCompetition +
        "/" +
        gender,
      method: "get",
      dataType: "html",
      beforeSend: function(xhr) {
        $("#concurrent_loader").show();
        $("#concurrentSearchResultList option").attr("disabled", "disabled");
      },
      complete: function() {
        $("#concurrent_loader").hide();
      },
    });

    request.done(function(msg) {
      if ($("#concurrentGet").val().length > 0) {
        $("#concurrentGetResultList").show();
      } else {
        $("#concurrentGetResultList").hide();
        $("#concurrentSelect")
          .children()
          .remove();
      }

      $("#concurrentSelect")
        .children()
        .remove();
      $(msg)
        .find("object")
        .each(function() {
          var concurrent = "";
          $(this)
            .find("field")
            .each(function() {
              concurrent += " " + $(this).text();
            });
          $("#concurrentSelect").append(
            new Option(concurrent, $(this).attr("pk"))
          );
          var id = $(this).attr("pk");
        });
    });

    request.fail(function(jqXHR, textStatus) {
      alert("Request failed: " + textStatus);
    });
  }, 400);
});

$("#concurrentSelect").change(function() {
  var value = $(this).val();
  var text = $(this)
    .find("option:selected")
    .text();
  var message = "Voulez-vous ajouter \n" + text + " ? ";
  //   if (confirm(message)) {
  $("#concurrentGetResultList").hide();
  $("#concurrentGet").val("");
  currentCompetition = $("#currentCompetiton").val();

  var request = $.ajax({
    url: "/scoresheet/event/add/" + value + "/" + currentCompetition,
    type: "GET",
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });
  //   } else {
  //   }
});

//
// COMPETITION
//

//
// EVENT
//

eventViewDrawForm = function(id) {
  $("#value_draw_" + id).hide();
  $("#form_draw_" + id).show();
  $("#input_draw_" + id).select();
  $("#input_draw_" + id).keypress(function(event) {
    var keycode = event.keyCode ? event.keyCode : event.which;
    if (keycode == "13") {
      eventSaveDraw(id);
    }
  });
};

eventSaveDraw = function(id) {
  var buffer = $("#input_draw_" + id).val();
  if (!buffer) {
    buffer = "0";
  }
  value = buffer.replace(",", ".");
  request = $.ajax({
    url: "/scoresheet/event/change/draw/" + value + "/" + id,
    type: "GET",
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });

  request.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
  });
};

eventViewWeightForm = function(id) {
  $("#value_weight_" + id).hide();
  $("#form_weight_" + id).show();
  $("#input_weight_" + id).select();

  $("#input_weight_" + id).keypress(function(event) {
    var keycode = event.keyCode ? event.keyCode : event.which;
    if (keycode == "13") {
      eventSaveWeight(id);
    }
  });
};

eventSaveWeight = function(id) {
  var buffer = $("#input_weight_" + id).val();
  if (!buffer) {
    buffer = "0";
  }
  value = buffer.replace(",", ".");
  request = $.ajax({
    url: "/scoresheet/event/change/weight/" + value + "/" + id,
    type: "GET",
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });

  request.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
  });
};

//
// Leader
//

$("input[id^=leaderGet-]").on("keyup", function(event) {
  event.preventDefault();
  id = (($(this)[0].id).split("-"))[1];
  console.log(id);
  motif = $(this).val()
  if (globalTimeout != null) {
    clearTimeout(globalTimeout);
  }

  if (event.which == 27) {
    $("#leaderGetResultList-"+id).hide();
    exit;
  }

  var motif = this.value;
  if (this.value.length < 2) {
    $("#leaderGetResultList-"+id).hide();
    $("#leaderSelect-"+id)
      .children()
      .remove();
    return;
  }

  currentCompetition = $("#currentCompetiton-"+id).val();
  currentLeadertypeid = $("#leadertypename-"+id).val();
  gender = $("#gender_id").val();
  globalTimeout = setTimeout(function() {
    globalTimeout = null;
    var request = $.ajax({
      url:
        "/scoresheet/leader/get/" +
        motif +
        "/" +
        currentCompetition +
        "/" +
        currentLeadertypeid,
      method: "get",
      dataType: "html",
      beforeSend: function(xhr) {
        $("#leader_loader-"+id).show();
        $("#leaderSearchResultList-"+id+" option").attr("disabled", "disabled");
      },
      complete: function() {
        $("#leader_loader-"+id).hide();
      },
    });

    request.done(function(msg) {
      if (motif.length > 0) {
        $("#leaderGetResultList-"+id).show();
      } else {
        $("#leaderGetResultList-"+id).hide();
        $("#leaderSelect-"+id)
          .children()
          .remove();
      }

      $("#leaderSelect-"+id)
        .children()
        .remove();
      $(msg)
        .find("object")
        .each(function() {
          var concurrent = "";
          $(this)
            .find("field")
            .each(function() {
              concurrent += " " + $(this).text();
            });
          $("#leaderSelect-"+id).append(new Option(concurrent, $(this).attr("pk")));
          // var id = $(this).attr("pk");
        });
    });

    request.fail(function(jqXHR, textStatus) {
      alert("Request failed: " + textStatus);
    });
  }, 400);
});

$("select[id^=leaderSelect-]").change(function() {
  id = (($(this)[0].id).split("-"))[1];
  var isteam = $("#isteam-"+id).val();
  var value = $(this).val();
  var text = $(this)
    .find("option:selected")
    .text();
  var leadertype = $("#leadertypename-"+id).val();
  var message = "Voulez-vous ajouter " + name + " \n" + text + " ? ";
  // if (confirm(message)) {
    $("#leaderGetResultList-"+id).hide();
    // $("#leaderGet").val("");
    currentCompetition = $("#currentCompetiton-"+id).val();

    var request = $.ajax({
      url:
        "/scoresheet/leader/add/" +
        value +
        "/" +
        currentCompetition +
        "/" +
        leadertype,
      type: "GET",
      beforeSend: function(xhr) {
        popupWait();
      },
    });

    request.done(function(msg) {
      // location.reload();
      var url = "/scoresheet/competition/view/" + currentCompetition;
      if (isteam == "True") {
        url = "/scoresheet/team/competition/view/" + currentCompetition;
      }
      $(location).attr("href", url);
    });
  // } else {
  // }
});

//
// MINMIUMWEIGHTCATEGORY
//

minimumweightcategoryViewForm = function(id) {
  $("#value_minimumweightcategory_" + id).hide();
  $("#form_minimumweightcategory_" + id).show();
  $("#input_minimumweightcategory_" + id).select();
  $("#input_minimumweightcategory_" + id).keypress(function(event) {
    var keycode = event.keyCode ? event.keyCode : event.which;
    if (keycode == "13") {
      minimumweightcategorySaveValue(id);
    }
  });
};

minimumweightcategorySaveValue = function(id) {
  value = $("#input_minimumweightcategory_" + id).val();
  if (!value) {
    value = "0";
  }
  var request = $.ajax({
    url: "/scoresheet/minimumweightcategory/change/value/" + value + "/" + id,
    type: "get",
    cache: false,
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload(false);
  });

  request.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
  });
};

//
// SEASON
//

$("input:radio[name=currentSeason]").change(function() {
  value = $("input:radio[name=currentSeason]:checked").val();
  location.href = value;
});

//
// TEAM
//

teamViewDrawForm = function(id) {
  $("#team_value_draw_" + id).hide();
  $("#team_form_draw_" + id).show();
  $("#team_input_draw_" + id).select();
  $("#team_input_draw_" + id).keypress(function(event) {
    var keycode = event.keyCode ? event.keyCode : event.which;
    if (keycode == "13") {
      teamSaveDraw(id);
    }
  });
};

teamSaveDraw = function(id) {
  var buffer = $("#team_input_draw_" + id).val();
  if (!buffer) {
    buffer = "0";
  }
  value = buffer.replace(",", ".");
  request = $.ajax({
    url: "/scoresheet/team/change/draw/" + value + "/" + id,
    type: "GET",
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });

  request.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
  });
};

teamViewNameForm = function(id) {
  $("#team_value_name_" + id).hide();
  $("#team_form_name_" + id).show();
  $("#team_input_name_" + id).select();
  $("#team_input_name_" + id).keypress(function(event) {
    var keycode = event.keyCode ? event.keyCode : event.which;
    if (keycode == "13") {
      teamSaveName(id);
    }
  });
};

teamSaveName = function(id) {
  var buffer = $("#team_input_name_" + id).val();
  if (!buffer) {
    buffer = "0";
  }
  value = buffer.replace(",", ".");
  request = $.ajax({
    url: "/scoresheet/team/change/name/" + value + "/" + id,
    type: "GET",
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });

  request.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
  });
};

$(".team").on("keyup", function(event) {
  id = $(this).attr("data-id");
  event.preventDefault();
  if (globalTimeout != null) {
    clearTimeout(globalTimeout);
  }

  if (event.which == 27) {
    $("#concurrentSearchResultList_" + id).hide();
    exit;
  }

  var motif = this.value;
  if (this.value.length < 2) {
    $("#concurrentSearchResultList_" + id).hide();
    $("#athleteSelect_" + id)
      .children()
      .remove();
    return;
  }

  currentCompetition = $("#currentCompetiton").val();
  gender = $("#gender_id").val();
  globalTimeout = setTimeout(function() {
    globalTimeout = null;
    var request = $.ajax({
      url:
        "/scoresheet/concurrent/get/" +
        $("#concurrent_search_" + id).val() +
        "/" +
        currentCompetition +
        "/" +
        gender,
      method: "get",
      dataType: "html",
      beforeSend: function(xhr) {
        $("#concurrent_loader_" + id).show();
        $("#concurrentSearchResultList_" + id + " option").attr(
          "disabled",
          "disabled"
        );
      },
      complete: function() {
        $("#concurrent_loader_" + id).hide();
      },
    });

    request.done(function(msg) {
      if ($("#concurrent_search_" + id).val().length > 0) {
        $("#concurrentSearchResultList_" + id).show();
      } else {
        $("#concurrentSearchResultList_" + id).hide();
        $("#athleteSelect_" + id)
          .children()
          .remove();
      }

      $("#athleteSelect_" + id)
        .children()
        .remove();
      $(msg)
        .find("object")
        .each(function() {
          var concurrent = "";
          $(this)
            .find("field")
            .each(function() {
              concurrent += " " + $(this).text();
            });
          $("#athleteSelect_" + id).append(
            new Option(concurrent, $(this).attr("pk"))
          );
        });
    });

    request.fail(function(jqXHR, textStatus) {
      alert("Request failed: " + textStatus);
    });
  }, 400);
});

$(".teamSelect").change(function() {
  id = $(this).attr("data-id");
  var value = $(this).val();
  var text = $(this)
    .find("option:selected")
    .text();
  var message = "Voulez-vous ajouter \n" + text + " ? ";

  // if (confirm(message))
  // {
  $("#concurrentSearchResultList").hide();
  $("#concurrent_search").val("");
  currentCompetition = $("#currentCompetiton").val();

  var request = $.ajax({
    url:
      "/scoresheet/event/add/team/" + value + "/" + currentCompetition + "/" + id,
    type: "GET",
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    location.reload();
  });
  // } else
  // {

  // }
});

$("#team_name").keypress(function(event) {
  var keycode = event.keyCode ? event.keyCode : event.which;
  if (keycode == "13") {
    $("#add_team").click();
  }
});

$("#add_team").click(function() {
  currentCompetition = $("#currentCompetiton").val();
  value = $("#team_name").val();
  if (!value || value.length === 0) {
    return;
  }

  var request = $.ajax({
    url: "/scoresheet/team/add/" + value + "/" + currentCompetition,
    type: "get",
    async: false,
    beforeSend: function(xhr) {
      popupWait();
    },
  });

  request.done(function(msg) {
    $("#team_name").val("");
    location.reload();
  });
});

//
// GLOBAL
//

popupWait = function() {
  titre = "Travail en cours";
  message = "Un instant S.V.P.";
  $("body").append(
    '<div id="overlay" style="background-color:transparent;position:absolute;top:0;left:0;height:100%;width:100%;z-index:999"></div>'
  );
  $("body").append('<div id="popupattente" title="' + titre + '"></div>');
  $("#popupattente").html(message);
  var popup;
  // var popup = $("#popupattente").dialog({
  //     autoOpen: true,
  //     top: 0,
  //     left:0,
  //     width: 400,
  //     dialogClass: 'no-close',
  //     hide: 'fade',
  // });

  // $("#popupattente").prev().addClass('ui-state-information');

  return popup;
};
