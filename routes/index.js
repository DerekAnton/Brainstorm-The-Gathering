//var User = require('../lib/tables').User;
var User = require('../lib/User/');
var Post = require('../lib/Post/');

var url = require('url');
var jsdom = require('jsdom');
var request = require('request');

exports.index = function(req, res)
{
	//check for cookie to see if user is logged in. If so, send them to the homepage instead of index (login) page.
	if(req.session.user == undefined){
		res.render('index', { title: 'SmallTalk', Post:[] });
	 }else{
	 	var posts = Post.getFollowedPosts(req.session.user.following, req.session.user.username);
		res.render('home', {title: "Welcome to SmallTalk", posts: posts});

	 }
};

exports.top10cards = function(req,res)
{
	navAndFetch(req, res, 'http://www.starcitygames.com/pages/decklists/', 'Nav');
};
var navAndFetch = function(req, res, url, navFetch)
{
	    request({uri: url}, function(err, response, body)
	    {
	      var self = this;
	      self.items = new Array();//I feel like I want to save my results in an array
	      if(err && response.statusCode !== 200){console.log('Request error.');}
	      jsdom.env(
	   			{
	               	html: body,
	               	scripts: ['http://code.jquery.com/jquery-1.6.min.js']
	            }, 
	            function(err, window)
	            {
	                var $ = window.jQuery;
	                console.log($('title').text());
	                res.end($('title').text());
	                if(navFetch === 'Nav')
	                {
	                	console.log($('#dynamicpage_standard_list p:nth-child(4) a:first-child').attr('href'));
	                }
	                if(navFetch === 'Fetch')
	                {

	                }
	            });
	    });
};




//Display the Sign Up view
exports.signup = function(req, res)
{
	res.render('signup', {title: 'Sign Up'});
};

//Submits a new post by the user to the database
exports.submitNewPost = function(req, res)
{
	var regexp = /%\w+/; // regular expression to accept a % followed by the set [a-z ,A-Z ,0-9,_] at least one or more times
	var postmsg = req.param("postTextField");
	var liked = req.param("like");
	var desiredlangs = regexp.exec(postmsg); // takes in the the postmsg and returns an array of any string that fits the regular expression defined above

	var newPost = {message:"", language:[], user:"", relationship: true}; // creates a new post object to be populated

	// if(desiredlangs != null)
	// {
	// 	for(var counter = 0; counter < desiredlangs.length; counter++)
	// 	{
	// 		desiredlangs[counter].slice(1, desiredlangs[counter].length);
	// 		/*if(!Post.getLanguage(desiredlangs[counter]))
	// 		{
	// 			this will be for the nice dropdown box, async javascript
	// 		}*/
	// 	}
	// }

	newPost.message = postmsg;
	newPost.user = req.session.user.username;
	newPost.language = desiredlangs;
	newPost.relationship = liked;
	Post.PostTable.push(newPost);
	


	res.redirect("/");

};

//Creates a session for the user upon entering username and password
exports.signin = function(req, res)
{//find user in database, compare 'stored' password with input password
		user = User.getUser(req.param("username"));

		if(user != undefined){
			if(user.password == req.param("password")){
				req.session.user = user;
				res.redirect('home', {})
			}
		}

	res.redirect('/');
}

//Ends the session for the user
exports.signout = function(req,res)
{//find user in database, compare 'stored' password with input password
	req.session.user = undefined;
	console.log("Logging Out");
	res.redirect('/');
}

//Allows the user to follow/unfollow other users
exports.toggleFollow = function(req, res){

	var toggled_user = req.param("toggle_follow_user");
	var current_user = req.session.user;

	var index = -1;

	if((index = (current_user.following.indexOf(toggled_user))) == -1){
		User.getUser(current_user.username).following.push(toggled_user)
	}else{
		User.getUser(current_user.username).following.splice(index,1)
	}

	req.session.user = User.getUser(current_user.username);

	console.log(req.session.user.following)
	res.redirect("/"+toggled_user+"/profile");
}

//Validates fields and creates a user in the temporary database
exports.createNewUser = function(req, res)
{
	//forEach(fucntion(objsinarray){objsinarray.getstuff})

	var username = req.param("username");
	var password = req.param("password");
	var email = req.param("email");
	var firstname = req.param("firstname");
	var lastname = req.param("lastname");

	var user = {username: "",password: "",email: "",firstname: "",lastname: "",followers: [],following: []};
	user.username = username;
	user.password = password;
	user.email = email;
	user.firstname = firstname;//no validations 
	user.lastname = lastname;// for real names, just add to user object

	if(user.username != "" && user.password != "" && user.email != "")
	{	
		tabled_user = User.getUser(user.username);

		if(tabled_user != undefined){//username is already taken
			res.redirect("/signup"); //if signup is successful, send them to home(cookie required)
		}
		else
		{
			User.UserTable.push(user);
			req.session.user = user;
			res.redirect("/");
		}
	}
	else
	{
		res.redirect("/signup");
	}
};
