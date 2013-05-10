function createUser() {
	var first_name = $("#first_name").val();
	var email = $("#email").val();
	var last_name = $("#last_name").val();
	var password = $("#password").val();
	$.post("/create_user", {
		"email" : email,
		"password" : password,
		"first_name" : first_name,
		"last_name" : last_name
	})
	.done(function(data) {
		if (data === "Success")
			window.location.href = "/";
	})
}

function createCircle() {
	var name = $("#name").val();
	var description = $("#description").val();
	var email = localStorage.getItem("email");
	$.post("/create_circle", {
		"name" : name,
		"email" : email,
		"description" : description
	}).done(function(data) {
		window.location.href = "/";
	}).fail(function() {
		$("body").html("Try Again!");
	})
}

function createContact() {
	var selectedCircles = 
		$("input[name=user_circles]:checked").map(
		     function () {return this.value;}).get().join(",");
    name = $("#name").val();
	email = $("#email").val();
	$.post("/create_contact", {
		"name": name,
		"circles": selectedCircles,
		"email": email,
		"user_email": localStorage.getItem("email")
	}).done(function(data) {
		if(data === "Failure")
			alert("Contact not valid")
		window.location.href = "/";
	}).fail(function() {
		$("body").html("Try Again!");
	})
}

function postAnswer(question_id) {
	description = $("#text").val();
	question_id = 
	$.post("/post_answer",
	          {"email": localStorage.getItem("email"),
	           "question_id": question_id,
	           "description": description,
	           "name": localStorage.getItem("name")})
	.done(function(data){
		window.location.reload(true)
	 })
	.fail(function(data) {
	 })
}

function createQuestion() {
	   var selectedCircles = $("input[name=user_circles]:checked").map(
		     function () {return this.value;}).get().join(",");
	   description = $("#description").val();
	   $.post("/post_question",{
		        "circles": selectedCircles,
		        "email": localStorage.getItem('email'),
		        "description": description,
		        "location": localStorage.getItem('location')})
	   .done(function(data) {
		   window.location.href = "/"
	   })
}

function doLogin() {
	var email = $("#email").val();
	var password = $("#password").val();
	$.post("/login", {
		'email': email,
		'password': password
		}).done(function(data) {
			  var user_data = JSON.parse(data)
              localStorage["email"] = user_data.email;
              localStorage["name"] = user_data.name;
              window.location.href = "/home?email=" + email;
		}).fail(function(data) {
		})
}

function navigateToViewContacts() {
    window.location.href = "/view_contacts?email=" 
    	+ localStorage.getItem('email')
}

function navigateToNotifications() {
	window.location.href = "/view_notifications?email=" 
    	+ localStorage.getItem('email')
}

function navigateToFavorites() {
	window.location.href = "/home?favorites=1&email=" 
		+ localStorage.getItem('email')
}
function addFavoriteEventListener() {
	$(".favorite").click(function(event) {
		$(this).find('img').toggle();
		var question_id = $(this).attr("id")
		$.post("/mark_favorite", {
			'email': localStorage.getItem('email'),
			'question_id': question_id
		})
	    .done(function(data) {
	    })
	   .fail(function(data) {
	   })
    })
}

function updateVoteCounter(answer_id, question_id, vote_count) {
	
	$(".vote_count").each(function(){
		var id = answer_id + " " + question_id
		if($(this).attr("id") === id) {
			$(this).html(vote_count)
		}
	})
}

function refresh() {
	window.location.reload(true)
}
function refreshIfNewAnswer(question_id) {
    var selector = "#" + question_id;
    if($(selector).length > 0)
    	refresh()
}


function addVoteEventListener() {
	$('.upvote_link').click( function(event) {
		var ids = $(this).attr('id').split(" ")
		var question_id = ids[1]
		var answer_id = ids[0]
		var state = 1;
		if(this.innerHTML.indexOf('Upvoted(Undo') !== -1){
			this.innerHTML='Upvote';
			state = -1;
		}
		else{
			this.innerHTML='Upvoted(Undo)';
			state = 1;
		}
		$.post("/mark_vote", {
			'email': localStorage.getItem('email'),
			'name': localStorage.getItem('name'),
			'answer_id': answer_id,
			'question_id': question_id,
			'state': state
	    })
	    .done(function(data) {
	    })
	    .fail(function(data) {
	    })
	});
}

function determineGeoLocation() {
    if (navigator.geolocation) {
    	navigator.geolocation.getCurrentPosition(populateLocationName);
    } else {
    	alert("Geolocation is not supported by this browser.");
    }
}

function populateLocationName(position) {
	var latlng = position.coords.latitude + "," + position.coords.longitude
	var location = "Not determined"
    $.get("http://maps.googleapis.com/maps/api/geocode/json?latlng="+latlng+"&sensor=false")
    .done(function(data) {
    	var address = data["results"][0]["formatted_address"].split(",")
    	localStorage["location"] = address[1];
    })
    .fail(function(data) {
    })  
}

function displayQuestions(authors) {
	var post_authors = authors
	$(".author").each(function(){
		var cur_author = $(this).attr("id");
		if($.inArray(cur_author, post_authors) >= 0) {
			$(this).show()
		}
		else {
			$(this).hide()
		}
	})
}

function addStreamChangeListener() {
	$("#stream").change(function(data) {
		$("#stream option:selected").each(function () {
            var circle = $(this).text();
            $.post("/circle_members", {
            	      "email": localStorage.getItem("email"),
            	      "circle": circle
            	}
            )
            .done(function(data){
            	authors = JSON.parse(data)
            	if(circle === "All Circles")
            		authors.push(localStorage.getItem("email"))
            	displayQuestions(authors)
            })
        });
	})
}

$(document).ready(function() {
	addFavoriteEventListener();
	addStreamChangeListener();
	addVoteEventListener();
	determineGeoLocation();
});