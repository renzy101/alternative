angular.module('MyApp')
  .controller('SignupCtrl', function($scope, $location, $auth, toastr,$http) {
    $scope.signup = function() {

      
      $auth.signup($scope.user)

        .then(function(response) {
          $http.post('/api/getUser', {"email": $scope.user['email']})
              .success(function (data) {
                //console.log(data);
                localStorage.currentUser=data.userid;
              })
              .error(function(error) {
                      console.log(error);
                                              
              });

          $auth.setToken(response);
          $location.path('/');
          toastr.info('You have successfully created a new account and have been signed-in');
        })
        .catch(function(response) {
          toastr.error(response.data.message);
        });
    };
  });