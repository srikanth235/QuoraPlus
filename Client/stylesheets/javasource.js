function createUser() {
	first_name = $("#first_name").val();
	email = $("#email").val();
	last_name = $("#last_name").val();
	password = $("#password").val();
	$.post("/create_user", {
		"email" : email,
		"password" : password,
		"first_name" : first_name,
		"last_name" : last_name
	})
	.done(function(data) {
		if (data === "Success")
			window.location.href = "/html/login.html";
	})
}
function createCircle() {
	name = $("#name").val();
	description = $("#description").val();
	email = localStorage.getItem("email");
	$.post("/create_circle", {
		"name" : name + "_" + email,
		"email" : email,
		"description" : description
	}).done(function(data) {
		alert(data);
		window.location.href = "/html/index.html";
	}).fail(function() {
		$("body").html("Try Again!");
	})
}
function createContact() {
	name = $("#name").val();
	email = $("#email").val();
	circles = $("#circles").val();
	$.post("/create_contact", {
		"name" : name,
		"circles" : JSON.stringify([ circles ]),
		"email" : email,
		"user_email" : localStorage.getItem("email")
	}).done(function(data) {
		alert(data)
		window.location.href = "/html/ViewContacts.html";
	}).fail(function() {
		alert("fail")
		$("body").html("Try Again!");
	})
}
function postAnswer() {
	description = $("#description").val();
	$.post("/post_question",
	          {"user_id":localstorage.getItem(email) , "description": description , "name":localstorage.getItem(name)})
}
function createQuestion() {
	   circles = $("#circles").val();
	   description = $("#description").val();
	   $.post("/post_question",// inserting q id?
	          {"circles": circles, "description": description})
}
$(document).ready(function() {
	$("#favorite").click(function() {
		$(this).find('img').toggle();
	});
	$('#upvote_link').click( function(event) {
	    
		var link_content = document.getElementById("u1");
		if(link_content.innerHTML === 'Undo')
			link_content.innerHTML='UpVote';
		else
			link_content.innerHTML='Undo';			
	});
});

