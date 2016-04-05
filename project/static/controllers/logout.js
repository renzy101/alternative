angular.module('MyApp')
  .controller('LogoutCtrl', function($location, $auth, toastr) {
  	localStorage.removeItem('currentUser')
    if (!$auth.isAuthenticated()) { return; }
    $auth.logout()
      .then(function() {
        toastr.info('You have been logged out');
        $location.path('/');
      });
  });