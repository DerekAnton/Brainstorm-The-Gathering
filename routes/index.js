
/*
 * GET home page.
 */

exports.index = function(req, res){
  res.render('signin');
};


exports.home = function(req, res){
	res.render('home');
}

exports.register = function(req, res){
	res.render('register');
}