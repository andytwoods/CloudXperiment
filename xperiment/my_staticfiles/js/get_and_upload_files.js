var get_and_upload_files = (function(){
    var api = {}

    var input
    var command
    var github_get_files_action_id
    var zip_admin
    var github_admin

    api.setup = function(input_group_id, github_menu_dropdown_id, _github_get_files_action_id, _command, zip_packages){
        input = $(input_group_id)
        command = _command
        github_get_files_action_id = _github_get_files_action_id

        $(github_menu_dropdown_id + " li a").click(function(){
            var txt = $(this).text()
            var repos=  $(this).data('repo-name')

            $(input).val(txt)
            $(input).data('repo-name', repos)
        })

        $(github_get_files_action_id).click(function(){
            var repos = $(input).data('repo-name')
            repos = 'https://github.com/andytwoods/jsPsychXptComms/archive/master.zip'
            if(repos==undefined || repos.length==0)return
            disable(true)
            $(this).prop('disabled', true)

        
            if(zip_admin == undefined) zip_admin = ZipAdmin()

            var reposArr = repos.split(",")
            for(var repo_i in reposArr){
                var repo = reposArr[repo_i]

                zip_admin.load(repo)
                return
            }

        })
    }

    function disable(yes){
         $(github_get_files_action_id).prop('disabled', yes)
    }

    function callback(success, data){
        disable(false)
        if(success=='success'){

        }
    }



    return api
}())

var GithubAdmin = (function(){
    var api = {}

    const gh = new GitHub();


    api.load = function(repo_name){


        var found = gh.search({'name':repo_name})


        var found = gh.search({'query': repo_name})
        console.log({'query':found})


    }

    return api
})

var ZipAdmin = (function(){
    var api = {}

    var buffer = []

    api.load = function(url){

        console.log(343,url)
        JSZipUtils.getBinaryContent(url, function(err, data){
            console.log(err, data)
        })
    }



    return api
})