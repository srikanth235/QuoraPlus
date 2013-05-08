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

function postAnswer() {
	description = $("#description").val();
	$.post("/post_question",
	          {"user_id":localstorage.getItem(email) , "description": description , "name":localstorage.getItem(name)})
}

function createQuestion() {
	   var selectedCircles = $("input[name=user_circles]:checked").map(
		     function () {return this.value;}).get().join(",");
	   description = $("#description").val();
	   $.post("/post_question",{
		        "circles": selectedCircles,
		        "email": localStorage.getItem('email'),
		        "description": description})
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
              localStorage["screen_name"] = user_data.screen_name;
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

$(document).ready(function() {
	$("#favorite").click(function() {
		$(this).find('img').toggle();
	});
	$('#upvote_link').click( function(event) {
	    
		var link_content = document.getElementById("u1");
		var vote_count =  document.getElementById("votecount");
		var num = vote_count.innerHTML;
		if(link_content.innerHTML === 'Undo'){
			link_content.innerHTML='UpVote';
			num--;
		}
		else{
			link_content.innerHTML='Undo';
			num++;
		}
		vote_count.innerHTML=num;
	});
	   
	
});