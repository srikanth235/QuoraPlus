/*** 
 * 
 * All custom written javascript functionalities 
 * across all HTML pages goes here.
 * 
 * **/

ls = localStorage
    	    
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
			window.location.href = "/html/login.html";
		else
			alert("Failure")
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
		alert(data);
		window.location.href = "/html/index.html";
	}).fail(function() {
		$("body").html("<h1>Try Again!</h1>");
	})
}

function createContact() {
	var name = $("#name").val();
	var email = $("#email").val();
	var circles = $("#circles").val()
	circles = ["Family"]
	$.post("/create_contact", {
		"name" : name,
		"circles" : JSON.stringify(circles),
		"email" : email,
		"user_email" : localStorage.getItem("email")
	}).done(function(data) {
		window.location.href = "/html/ViewContacts.html";
	}).fail(function() {
		alert("fail")
		$("body").html("Try Again!");
	})
}

function postAnswer() {
	var description = $("#description").val();
	$.post("/post_question",
	          {"user_id":localstorage.getItem(email) , "description": description , "name":localstorage.getItem(name)})
}

function createQuestion() {
	var circles = $("#circles").val();
	var description = $("#description").val();
	$.post("/post_question",// inserting q id?
	       {"circles": circles, "description": description})
}

function doLogin() {
	var email = $("#email").val();
	var password = $("#password").val();
	$.post("/login",
		    {"email": email, "password": password}).
    done(function(data) {
    	    var properties = JSON.parse(data);
    	    ls.setItem("email", properties["email"]);
    	    ls.setItem("screen_name", properties["screen_name"])
    	    window.location.href = "/?auth=1";
         }).
    fail(function() { alert("Failure"); })
}

function displayContacts() {
	window.location.href = "/html/CreateContact.html"
}

function displayPostQuestion(){
	window.location.href = '/html/post_question.html';
}

function displayNotifications() {
	window.location.href = '/html/NotificationsPage.html';
}

function displayMoreNavigation() {
	window.location.href = '/html/NavigationPage.html';
}

function displayCreateContact() {
	window.location.href = '/html/CreateContact.html';
}

function addFavoriteEventListener() {
	$("#favorite").click(function() {
		$(this).find('img').toggle();
	});
}

function addVoteEventListener() {
	$('#upvote_link').click( function(event) {
		var link_content = document.getElementById("u1");
		if(link_content.innerHTML === 'Undo')
			link_content.innerHTML='UpVote';
		else
			link_content.innerHTML='Undo';			
	});
}

$(document).ready(function() {
    addFavoriteEventListener();
    addVoteEventListener();
});

