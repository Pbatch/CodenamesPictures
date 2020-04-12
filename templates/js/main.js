$(document).ready(function(){

  //Generate a clue
  function generate_clue() {
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
          $("#clue").html(`<img src="static/pictures/${clue}.jpg" id="clue" class="picture">`);
      }
    });
  }

  //Update picture
  function update_picture(id) {

    // Don't update a picture if it is active
    if (board[id].active == true) {
        return;
    }

    //Set the picture to active
    board[id].active = true;

    //Change the class of the picture
    $("#"+id).attr('class', 'active_picture');

    //Change the css of the frame
    $("#frame"+id).css({
    "border-style": "solid",
    "border-color": board[id].colour
    });

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
      var final_text = 'You win!'
      end = true;
    }
    else if (red_remaining == 0 || assassin_remaining == 0) {
      var final_text = 'You lose...';
      end = true;
    }

    if (end == true) {
      //Change the clue text
      $('#clue').html(final_text);
      //Stop picture and end turn clicks
      $('.picture').css('pointer-events', 'none');
      $('#end_turn').css('pointer-events', 'none');
      //Show all the remaining pictures
      for (i = 1; i < 26; i++) {
        update_picture(i);
      }
    }

    return end;
   }


  //Computer turn
  function computer_turn() {
    //Get a computer sequence
    $.ajax({
       type:'POST',
       url: "{{ url_for('computer_turn')}}",
       contentType: "application/json; charset=utf-8",
       dataType: "html",
       data: JSON.stringify(board),
       success: async function(sequence){
         var sequence = JSON.parse(sequence).sequence;

         console.log(sequence);

         //Apply the sequence
         var sequence_length = sequence.length;
         for (i = 0; i < sequence_length; i++) {
            update_picture(sequence[i]);
            if (check_end() == true) {
                return;
            }
         }
         //Generate a new clue
         if (check_end() == false) {
            generate_clue();
         }
       }
    });
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
  generate_clue();

  /*
  Click events
  */

  //Picture behaviour
  $('.picture').click(function() {
     //Get the id of the picture
     var id = $(this).attr('id');

    //Update the clicked picture
    update_picture(id);

    //Check if the game has ended
    check_end();

    //If we don't choose a blue picture, it's the computer's turn
    if (board[id].type != "blue") {
      computer_turn();
    }
  });

  //Reset button behaviour
  $('#reset').click(function() {
     $.ajax({
        type:'POST',
        url: "/",
        dataType: "html",
        success: function(response){
          $("body").html(response);
        }
    });
  });

  //End turn button behaviour
  $('#end_turn').click(function() {
    computer_turn();
  })

});