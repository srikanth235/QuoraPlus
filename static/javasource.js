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
		window.location.href = "/view_contacts";
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
		alert(data)
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
		        "locaiont": localStorage.getItem('location')})
	   .done(function(data) {
		   alert(data)
		   window.location.href = "/"
	   })
}

function QuestionPage(){
	    return false;
}

function displayPage() {
    var questionId=123;//This Id is given by the server
    var url = "http://"+window.location.host+"/Client"+"/"+questionId;    
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
              localStorage["name"] = user_data.screen_name;
              window.location.href = "/home?user=" + email;
		}).fail(function(data) {
			   alert("failure")
		})
}

function navigateToViewContacts() {
    window.location.href = "/view_contacts?email=" 
    	+ localStorage.getItem('email')
}

function navigateToNotifications() {
	window.location.href = "/notifications?email=" 
    	+ localStorage.getItem('email')
}

function addFavoriteEventListener() {
	$(".favorite").click(function() {
		$(this).find('img').toggle();
		var question_id = $(this).attr("id")
		$.post("/mark_favorite", {
			'email': localStorage.getItem('email'),
			'question_id': question_id
		})
	    .done(function(data) {
			alert(data)
	    })
	   .fail(function(data) {
			alert("Failure");
	   })
    })
}

function addVoteEventListener() {
	$('.upvote_link').click( function(event) {
		var answer_id = $(this).attr('id')
		var state = 1;
		if(this.innerHTML.indexOf('Upvoted(Undo') !== -1){
			this.innerHTML='Upvote';
			state = 1;
		}
		else{
			this.innerHTML='Upvoted(Undo)';
			state = -1;
		}
		alert(answer_id)
		$.post("/mark_vote", {
			'email': localStorage.getItem('email'),
			'name': localStorage.getItem('name'),
			'answer_id': answer_id,
			'state': state
	    })
	    .done(function(data) {
	    	alert(data)
	    })
	    .fail(function(data) {
	    	alert("Fail")
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

$(document).ready(function() {
	addFavoriteEventListener();
	addVoteEventListener();
	determineGeoLocation();
});