//Equivalent to time.sleep(). Only works on async functions.
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

$(document).ready(function(){
  //Update picture
  function update_picture(id) {

    //Set the picture to active
    board[id].active = true;

    //Change the opacity
    $("#"+id).css({
    "opacity": 0.1,
    "pointer-events": "none"});

    //Decrement the appropriate count
    if (board[id].type == "blue") {
        blue_remaining -= 1;
        $('#blue').html(blue_remaining);
    } else if (board[id].type == "red") {
        red_remaining -= 1;
        $('#red').html(red_remaining);
    } else if (board[id].type == "neutral"){
        neutral_remaining -= 1;
    } else if (board[id].type == "assassin"){
        assassin_remaining -= 1;
    }
  }

  //Check if the game has ended
  function check_end() {
    var end = false;
    if (blue_remaining == 0) {
      var end = true;
    }
    //The computer never chooses the assassin so no assassin guarantees a loss
    else if (red_remaining == 0 || assassin_remaining == 0) {
      var end = true;
    }
    if (end == true) {
      //Reveal the pictures
      for (i = 1; i < 26; i++) {
        if (board[i].active == false) {
            update_picture(i);
        }
      }
    }
    return end;
  }

  /*
  Setup
  */

  var board = {{board|tojson|safe}};
  var remaining_guesses = 0;
  var blue_remaining = 9;
  var red_remaining = 8;
  var neutral_remaining = 7;
  var assassin_remaining = 1;

  /*
  Click events
  */

  //Card behaviour
  $('.picture').click(function() {
     //Get the id of the picture
     var id = $(this).attr('id');

     if (board[id].active == false) {
        //Update the clicked picture
        update_picture(id);
        check_end();
     }
  });

  //Clue button behaviour
  $.ajax({
    type:'POST',
    url: "{{ url_for('clue')}}",
    contentType: "application/json; charset=utf-8",
    dataType: "html",
    data: JSON.stringify(board),
    success: function(clue_details){
        var clue_details = JSON.parse(clue_details);
        var clue = clue_details.clue;

        //Add the clue to the list of invalid guesses
        board[0]["invalid_guesses"].push(clue);

        //Load in the picture corresponding to the given clue
        $("#clue").html(`<img src="${clue}" id="clue" class="picture">`)
    }
  });
});