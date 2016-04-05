angular.module('MyApp').controller('WishCtrl' , ['$scope','$http','$log','$window', function ($scope,$http,$log,$window) {
	var userid= localStorage.getItem('currentUser');
	$http.get('/api/user/'+userid+'/wishlist')
        .success(function(data) {
        	$scope.wishes = data.data.wishes;

        	$log.log($scope.wishes);
        	
      })
        .error(function(error) {
        $log.log(error);
      });
        $scope.go = function() {
   			$window.location.href = '/#/add';
   };






}]);