from data.usersAndPassword import deviceIdOf, passwordOf, pkOf, userAgentOf
from InstagramAPI.InstagramAPI import InstagramAPI
import re
import config
import time
import json
import random


class Instafollow():
    api: InstagramAPI = InstagramAPI
    current_Instafollow = None
    Instafollows: list = []
    res: str = ''
    run = True
    speakToMe = config.speakToMe

    def __new__(cls, userName=None, proxy=None):
        if not Instafollow.run:
            if Instafollow.current_Instafollow.finish_after:
                if userName != Instafollow.current_Instafollow.userName:
                    config.stopRunBackground()
                    exit()
            else:
                config.stopRunBackground()
                exit()
        if userName == None:
            return super(Instafollow, cls).__new__(cls)
        if Instafollow.current_Instafollow != None:
            if Instafollow.current_Instafollow.userName == userName:
                return Instafollow.current_Instafollow
        for thisInstafollow in Instafollow.Instafollows:
            if thisInstafollow.userName == userName:
                Instafollow.current_Instafollow = thisInstafollow
                Instafollow.print_and_log(
                    "switch to", userName, underLine=True, res=Instafollow.current_Instafollow.res)
                return Instafollow.current_Instafollow
        else:
            return super(Instafollow, cls).__new__(cls)

    def __init__(self, userName, passwordOf=passwordOf, pkOf=pkOf, userAgentOf=userAgentOf, deviceIdOf=deviceIdOf,  proxy=None):
        self.stop = False
        if not Instafollow.run:
            if Instafollow.current_Instafollow.finish_after:
                if userName != Instafollow.current_Instafollow.userName:
                    config.stopRunBackground()
                    exit()
            else:
                config.stopRunBackground()
                exit()
        if Instafollow.current_Instafollow != None and Instafollow.current_Instafollow.userName == userName:
            if Instafollow.current_Instafollow.end:
                Instafollow.current_Instafollow.login = False
            return
        if len(Instafollow.Instafollows) > 5:
            Instafollow.Instafollows.pop(0)
        Instafollow.current_Instafollow = self
        Instafollow.Instafollows.append(self)
        self.InstagramAPI = InstagramAPI
        self.startTime = time.asctime()
        self.userName = userName
        self.res = ''
        self.login = False
        self.pause = False
        self.end = False
        self.proxy = False
        self.finish_after = False
        self.canGetCommenters = True
        self.users_i_follow = []
        if (passwordOf(userName)) == False:
            self.print_and_log("user", userName, "not found", warning=True)
            Instafollow.Instafollows.remove(self)
            return
        self.passwordOf = passwordOf
        self.pkOf = pkOf
        self.api = Instafollow.api(username=userName, password=passwordOf(userName), device_id=deviceIdOf(
            userName), user_agent=userAgentOf(userName), debug=False, IGDataPath=None)
        if not proxy:
            proxy = config.getProxy()
            if proxy:
                self.proxy = True
                self.api.setProxy(proxy)
        try:
            self.login = self.api.login()
        finally:
            if (self.login):
                self.print_and_log("Login to", userName,
                                   "success!", underLine=True)
                self.print_and_log("starting Instafollow")
            else:
                try:
                    challenge_required = (
                        self.api.LastJson['message'] == 'challenge_required')
                except KeyError:
                    self.print_and_log(
                        "Can't login to", self.userName, ", unknown problam !")
                    return
                if challenge_required:
                    self.print_and_log("Can't login to", self.userName,
                                       "too many requests or first login , try again tomorrow!")
                    return
                self.print_and_log(
                    "Incorrect password Can't login to", self.userName, "!")
                return
        self.users = []
        self.blockedMe = []

    def OpenAccount(self, PublicOrPrivate):
        if PublicOrPrivate:
            self.api.setPublicAccount()
            self.print_and_log("set", self.userName, "as a Public Account")
        else:
            self.api.setPrivateAccount()
            self.print_and_log("set", self.userName, "as a setPrivate Account")

    def print_and_log(self, *text, res=False, underLine=False, DevMode=False, warning=False, speak=False):
        if DevMode and not config.isDevMOde():
            return
        text = ' '.join(str(r) for r in text)
        print("[", time.strftime("%H:%M:%S"), "]", text)
        if underLine:
            print((len(text) + 13) * '=')
        if warning:
            text = "⚠️  " + text + " ⚠️"
        text += '\n'
        if speak:
            Instafollow.speakToMe(text)
        if res == False:
            if not self:
                Instafollow.res += text
                return
            self.res += text
            return
        res += text

    def listen(self):
        count = 0
        length = len("pause program")
        if self.pause:
            print("pause program")
        wait = False
        while (self.pause):
            wait = True
            count += 1
            print(".", end="")
            if count % length == 0:
                print(" wait for", count, "sec", end="\r")
            time.sleep(1)
        if wait:
            print("wait for", count, "sec")
        if self.stop:
            return True

    def timeToSleep(self, timeToSleep: int, randomList: list = []):
        if timeToSleep:
            if randomList and not random.choice(randomList):
                return
            if self.proxy:
                timeToSleep //= 2
                if timeToSleep < 1:
                    timeToSleep = 1
            if randomList:
                timeToSleep * sum(randomList)
            time.sleep(
                random.randrange(timeToSleep))
            print(" sleep for", timeToSleep, "sec", end='\r')

    def loopUsers(self, users, send=False, follow=False, like=False, comment=False, thatComment=False,
                  no_duplicate_comments=False, text: str = None, mediaId=None, timeToSleep=False):

        users_i_send = []
        users_i_follow = []
        followCount = 0
        likesIDo = 0
        commentsIDo = 0
        user_i_visit_count = 0
        messagesCount = 0
        loopIndex = 0
        if type(text) == list:
            for i in text:
                if type(text) == str:
                    lines = text.splitlines()
                    if lines[0] == '':
                        lines.pop(0)
                        text = "\n".join(lines)
        if not users:
            print("there is no users to loop through")
            return[False, False]
        for i in users:
            if self.listen():
                break
            if follow:
                if not self.api.follow(i[0]):
                    print("follow blocked to", i[1])
                    follow = False
                    continue
                followCount += 1
                print("follow number", followCount, "to", i[1])
                users_i_follow.append((i[0], i[1]))
            if (like or comment) is True and i[2] is False:
                visit = self.doLikesToThisUser(
                    userIWantToLike=i[0], userName=i[1], doComment=comment, thatComment=thatComment, doLike=like, no_duplicate_comments=no_duplicate_comments,
                    timeToSleep=timeToSleep)
                if not visit[0] or not visit[1]:
                    if not visit[0]:
                        like = False
                    else:
                        likesIDo += visit[2]
                    if not visit[1]:
                        comment = False
                    else:
                        commentsIDo += visit[3]
                else:
                    likesIDo += visit[2]
                    commentsIDo += visit[3]
                user_i_visit_count += 1
            if send and random.choice([True, False]):
                if not text:
                    send = False
                message_text = random.choice(text)
                links = re.findall(
                    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)
                if random.choice([True, False]) and not self.sendMassage(userIWantToSendPk=i[0], text=message_text, mediaId=mediaId, link=links or None):
                    print("link message" if links else "message", "number", messagesCount,
                          "to", i[1], "blocked")
                    send = False
                    continue
                messagesCount += 1
                print("send massage number", messagesCount, "to", i[1])
                users_i_send.append((i[0], i[1], i[2]))
            if (send or follow or like or comment) is False:
                break
            loopIndex = users.index(i)
            print(" index", loopIndex, self.userName, end='\r')
            self.timeToSleep(timeToSleep=timeToSleep, randomList=[
                             send, follow, like, comment])
            # sys.stdout.write("\033[F") # back last line
            # sys.stdout.write("\033[K") # kill line
        if users_i_follow:
            print("\n\n", users_i_follow, "\n\n")
        print("loop", loopIndex, "users")
        if likesIDo != 0 or commentsIDo != 0:
            self.print_and_log("follow", followCount, "users likes",
                               likesIDo, "posts and commented", commentsIDo, "comments to", user_i_visit_count, "users")
        else:
            self.print_and_log("follow", followCount, "users")
        self.print_and_log(messagesCount, "number of messages was send")
        self.users_i_follow += users_i_follow
        return [users_i_follow, users_i_send]


    def get_users(self, functionIndex, userNameOrPk=False, limit=False, randomList=False, blackList=False, remove_follower_and_follower=True, no_anonymous_profile=True):
        # get username id
        username_id = False
        if (userNameOrPk == False):
            username_id = self.api.username_id
        if not isinstance(userNameOrPk, list):
            userNameOrPk = [userNameOrPk]
        random.shuffle(userNameOrPk)
        for userNameOrPk in userNameOrPk:
            if (type(userNameOrPk) != int):
                if userNameOrPk[0] == "@":
                    userNameOrPk = userNameOrPk[1:]

                try:
                    self.api.searchUsername(userNameOrPk)
                    username_id = self.api.LastJson['user']['pk']
                except:
                    self.print_and_log("can't get", userNameOrPk, "id")
            else:
                username_id = userNameOrPk
            if username_id:
                break
        print("visit", userNameOrPk)

        # get users
        userFollowings, userFollowers, userLikers, userCommenter = None, None, None, None
        obj = {
            0: userFollowings,
            1: userFollowers,
            2: userLikers,
            3: userCommenter

        }
        obj[functionIndex] = True
        userFollowings, userFollowers, userLikers, userCommenter = obj[0], obj[1], obj[2], obj[3]
        # print(userFollowers,userFollowings,userLikers)
        users = []
        countTry = 0
        while users == [] and countTry < 2:
            countTry += 1
            if limit and not userCommenter:
                maxid = ''
                for i in range(0, limit if limit > 1 else 3):
                    if userFollowings:
                        try:
                            self.api.getUserFollowings(username_id, maxid)
                        except Exception:
                            self.print_and_log(
                                "can't get", userNameOrPk, "followings")
                            break
                        else:
                            users += [(n["pk"], n['username'], n['is_private'])
                                      for n in self.api.LastJson['users'] if no_anonymous_profile and not n['has_anonymous_profile_picture']]
                            # print(users)
                        maxid = self.api.LastJson['next_max_id']
                    elif userFollowers:
                        try:
                            self.api.getUserFollowers(username_id, maxid)
                        except Exception:
                            self.print_and_log(
                                "can't get", userNameOrPk, "followers")
                            break
                        else:
                            users += [(n["pk"], n['username'], n['is_private'])
                                      for n in self.api.LastJson['users'] if no_anonymous_profile and not n['has_anonymous_profile_picture']]
                            # print(users)
                            maxid = self.api.LastJson['next_max_id']
                    if not maxid:
                        break
                self.print_and_log("get", len(users), userNameOrPk,
                                   "followers" if userFollowers else "followings")
            else:
                if userFollowings:
                    try:
                        users += [(n["pk"], n['username'], n['is_private'])
                                  for n in self.api.getTotalFollowings(username_id) if no_anonymous_profile and not n['has_anonymous_profile_picture']]
                    except Exception:
                        self.print_and_log(
                            "can't get", userNameOrPk, "total followings")
                    else:
                        self.print_and_log(
                            "get", userNameOrPk, "total followings")
                elif userFollowers:
                    try:
                        users += [(n["pk"], n['username'], n['is_private'])
                                  for n in self.api.getTotalFollowers(username_id) if no_anonymous_profile and not n['has_anonymous_profile_picture']]
                    except Exception:
                        self.print_and_log(
                            "can't get", userNameOrPk, "total followers")
                    else:
                        self.print_and_log(
                            "get", userNameOrPk, "total followers")
                elif userLikers:
                    photoIndex = False
                    try:
                        self.api.getUserFeed(username_id)  # Get user feed
                        photoIndex = random.randrange(
                            int(len(self.api.LastJson['items']) ** (1 / 3)))  # Get most recent post
                        media_id = self.api.LastJson['items'][photoIndex]['id']
                        self.api.getMediaLikers(media_id)
                        users = list(
                            map(self.getPk, self.api.LastJson['users']))
                    except Exception:
                        self.print_and_log("can't get", userNameOrPk,
                                           "total likers on post number", photoIndex)
                    else:
                        self.print_and_log("get", userNameOrPk,
                                           "total likers on post number", photoIndex)
                elif userCommenter:
                    photoIndex = False
                    if not limit:
                        try:
                            self.api.getUserFeed(username_id)  # Get user feed
                            photoIndex = random.randrange(
                                int(len(self.api.LastJson['items']) ** (1 / 3)))  # Get most recent post
                            media_id = self.api.LastJson['items'][photoIndex]['id']
                            users += self.getPostCommenters(mediaId=media_id)
                        except Exception:
                            self.print_and_log("can't get", userNameOrPk,
                                               "total commeters on post number", photoIndex)
                        else:
                            self.print_and_log("get", userNameOrPk,
                                               "total commeters on post number", photoIndex)
                    else:
                        try:
                            self.api.getUserFeed(username_id)  # Get user feed
                            feed = self.api.LastJson['items']
                            count = 0
                            while len(users) < limit * 100 and count < limit:
                                newPhotoIndex = None
                                for i in range(0, limit):
                                    newPhotoIndex = random.randrange(
                                        int(len(feed) ** (1 / 3)))  # Get most recent post
                                    if photoIndex != newPhotoIndex:
                                        break
                                if photoIndex == newPhotoIndex:
                                    break
                                photoIndex = newPhotoIndex
                                media_id = feed[photoIndex]['id']
                                users += self.getPostCommenters(
                                    mediaId=media_id)
                                count += 1
                        except Exception:
                            self.print_and_log("can't get", userNameOrPk,
                                               "total commeters on post number", photoIndex)
                        else:
                            self.print_and_log("get", userNameOrPk,
                                               "total commeters on post number", photoIndex)

        # random users
        if remove_follower_and_follower:
            try:
                myFollowings = map(
                    self.getPk, self.api.getTotalSelfFollowings())
                myFollowers = map(self.getPk, self.api.getTotalSelfFollowers())
            except KeyError:
                self.print_and_log("can't get followings")
                return
            users = list(set(users) - set(myFollowings) - set(myFollowers) - {(self.pkOf(
                self.userName), self.userName, True)} - {(self.pkOf(self.userName), self.userName, False)})
        if randomList:
            random.shuffle(users)
            print("random users")
        if blackList:
            for i in users:
                for ii in blackList:
                    if i[1] == ii:
                        users.remove(i)
                        break
        self.print_and_log(len(users), "users founed")
        return users

    def get_login_user_data(self):
        self.api.LastJson = None
        self.api.getProfileData()
        keys_i_want = ['phone_number', 'gender', 'email', 'username', 'full_name',
                       'is_private', 'pk', 'profile_pic_url', 'has_anonymous_profile_picture', 'biography']
        obj = {i: self.api.LastJson['user'][i]
               for i in keys_i_want if self.api.LastJson['user'][i] != ''}
        print(obj)
        return obj

    def unfollow_this_users(self, users, timeToSleep=False):
        myFollowings = [(n["pk"], n['username'])
                        for n in self.api.getTotalSelfFollowings()]
        unfollow_count = 0
        users_who_not_follow_anymore = list(set(users) - set(myFollowings))
        users = list(set(users) - set(users_who_not_follow_anymore))
        self.print_and_log(len(users), "i want to unfollow")
        for i in users:
            if i in myFollowings:
                if not self.api.unfollow(i[0]):
                    self.print_and_log(
                        "can't unfollow", i[1], "unfollow blocked!")
                    break
                unfollow_count += 1
                print("unfollow number", unfollow_count, 'to', i[1])
                if unfollow_count >= 300:
                    break
                self.timeToSleep(timeToSleep=timeToSleep,
                                 randomList=[False, True])
        self.print_and_log("unfollow", unfollow_count, "users")
        return users[unfollow_count:]

    def get_likers_list(self, userName, like, follow, comment, thatComment, timeToSleep=False):
        photoIndex = False
        usersNamesList = userName
        # while to handle if the user is private
        while (True):
            if type(usersNamesList) == list:
                if not usersNamesList:
                    usersNamesList = userName
                userName = random.choice(usersNamesList)
                usersNamesList.remove(userName)
                # print(userName)
            media_id = False
            try:
                self.api.searchUsername(userName)
                username_id = self.api.LastJson['user']['pk']  # Get user ID
                self.api.getUserFeed(username_id)  # Get user feed
                photoIndex = random.randrange(
                    int(len(self.api.LastJson['items']) ** (1 / 3)))
                media_id = self.api.LastJson['items'][photoIndex]['id']
            except:
                self.print_and_log(
                    "please remove private account", userName, warning=True)
                pass
            finally:
                if media_id:
                    break
            time.sleep(1)
        if usersNamesList:
            self.print_and_log("\nnew function get likers of", userName, "\n")
        # Get most recent post
        self.api.getMediaLikers(media_id)  # Get users who liked
        try:
            users = list(map(self.getPk, self.api.LastJson['users']))
            myFollowings = map(self.getPk, self.api.getTotalSelfFollowings())
            myFollowers = map(self.getPk, self.api.getTotalSelfFollowers())
        except:
            self.print_and_log(
                "something get wrong with geting the data to work")
            return

        pepole_i_do_not_want_follow = users[:]
        usersIWantToFollow = list(set(pepole_i_do_not_want_follow) - set(myFollowings) - set(myFollowers) - {(self.pkOf(
            self.userName), self.userName, True)} - {(self.pkOf(self.userName), self.userName, False)})
        usersIfollow = []
        if not users:
            return False
        likesIDo = 0
        commentsIDo = 0
        user_i_visit_count = 0
        followCount = 0
        self.print_and_log(len(users), "likers of post number", photoIndex + 1, "of", userName, "and", len(
            usersIWantToFollow), "users I want to loop through")
        for i in usersIWantToFollow:
            # print(i)
            if self.listen():
                break
            if not (like or follow or comment):
                break
            if follow:
                if not self.api.follow(i[0]):
                    print("follow blocked to", i[1])
                    follow = False
                    continue
                followCount += 1
                print("follow number", followCount, "to", i[1])
                usersIfollow.append((i[0], i[1]))
            if not (like or comment) or i[2]:
                continue
            visit = self.doLikesToThisUser(
                userIWantToLike=i[0], userName=i[1], doComment=comment, thatComment=thatComment, doLike=like,
                timeToSleep=timeToSleep)
            if not visit[0] or not visit[1]:
                if not visit[0]:
                    like = False
                else:
                    likesIDo += visit[2]
                if not visit[1]:
                    comment = False
                else:
                    commentsIDo += visit[3]
            else:
                likesIDo += visit[2]
                commentsIDo += visit[3]

            user_i_visit_count += 1

            print(" index", usersIWantToFollow.index(
                i), self.userName, end='\r')
            None if not timeToSleep else time.sleep(
                random.randrange(timeToSleep))
        if usersIfollow:
            print("\n\n", usersIfollow, "\n\n")
        if (likesIDo != 0):
            self.print_and_log("follow", followCount, "users likes",
                               likesIDo, "posts and commented", commentsIDo, "comments to", user_i_visit_count, "users")
        else:
            self.print_and_log("follow", followCount, "users")
        self.users_i_follow += usersIfollow
        return usersIfollow

    def getPostsByHashtags(self, text):
        self = self.api
        response = False
        if text[0] == '#':
            text = text[1:]
        try:
            response = self.s.get(
                "https://www.instagram.com/explore/tags/" + str(text) + "/?__a=1")
        except Exception as e:
            print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
            time.sleep(60)
        if response and response.status_code == 200:
            self.LastResponse = response

            def getMediaIdFromHastag(n):
                return n['node']['id'], n['node']['owner']['id'], n['node']['comments_disabled']

            self.LastJson = list(map(getMediaIdFromHastag, json.loads(response.text)[
                'graphql']['hashtag']['edge_hashtag_to_media']['edges']))
            return self.LastJson
        else:
            print("Request return " + str(response.status_code) + " error!")
            self.LastResponse = response
            self.LastJson = json.loads(response.text)

    def likePostByHastags(self, text, like=False, follow=False, comment=False, thatComment=False, goToUserFeed=False,
                          timeToSleep=False):
        posts = self.getPostsByHashtags(text)
        likedCount = 0
        commenetsCount = 0
        visitCount = 0
        followCount = 0
        visitCommentsCount = 0
        visitLikedCount = 0
        thatComment = thatComment if thatComment else ["❤", "🤍", '🖤', '❤️']
        self.print_and_log("going to loop on", len(
            posts), "posts of hastag", text)
        for i in posts:
            if not (like or comment or follow):
                break
            if follow:
                if not self.api.follow(i[1]):
                    print("follow blocked")
                    follow = False
                followCount += 1
                self.users_i_follow.append((i[1], False))
            if self.did_i_comment(i[0]):
                print("allready comment")
                continue
            if like:
                if not self.api.like(i[0]):
                    print("like blocked")
                    if "message" in self.api.LastJson.keys() and self.api.LastJson[
                            'message'] == 'Sorry, this media has been deleted':
                        print("this media has been delete")
                    else:
                        like = False
                else:
                    likedCount += 1
            if comment and not i[2]:
                if not self.api.comment(i[0], random.choice(thatComment)):
                    print("comments blocked")
                    if "feedback_title" in self.api.LastJson.keys() and (
                            self.api.LastJson['feedback_title'] == 'Commenting is Off' or self.api.LastJson[
                                'feedback_title'] == "Couldn't Post Your Comment"):
                        print("Commenting on this post is Off or limit")
                    elif "message" in self.api.LastJson.keys() and self.api.LastJson[
                            'message'] == 'Sorry, this media has been deleted':
                        print("this media has been delete")
                    else:
                        comment = False
                else:
                    commenetsCount += 1

            if goToUserFeed and (like or comment):
                visit = self.doLikesToThisUser(
                    int(i[1]), False, doLike=like, doComment=comment, thatComment=thatComment, timeToSleep=timeToSleep)
                if (visit[0] == False or visit[1] == False):
                    if visit[0] == False:
                        like = False
                    else:
                        visitLikedCount += visit[2]
                    if visit[1] == False:
                        comment = False
                    else:
                        visitCommentsCount += visit[3]
                else:
                    visitLikedCount += visit[2]
                    visitCommentsCount += visit[3]
                visitCount += 1
            print(" hastag post index", posts.index(i), self.userName, end='\r')
            self.timeToSleep(timeToSleep=timeToSleep,
                             randomList=[goToUserFeed, comment])
        if visitCount > 0:
            self.print_and_log("visit", visitCount, "users, liked", visitLikedCount,
                               "posts  comments", visitCommentsCount, "comments from visits")
        self.print_and_log("followed", followCount, "users, liked", likedCount,
                           "posts, comments", commenetsCount, "comments to the Hashtags posts")

    def getPostsByLocation(self, text):
        self = self.api
        response = False
        try:
            response = self.s.get("https://www.instagram.com/web/search/topsearch/?context=blended&query=" +
                                  str(text) + "&rank_token=" + str(self.rank_token) + "&include_reel=true")
            print("https://www.instagram.com/web/search/topsearch/?context=blended&query=" +
                  str(text) + "&rank_token=" + str(self.rank_token) + "&include_reel=true")
        except Exception as e:
            print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
            time.sleep(60)
        if response and response.status_code == 200:
            LocationId = json.loads(response.text)[
                'places'][0]['place']['location']['pk']
            print("Location Id", LocationId)
            try:
                response = self.s.get(
                    "https://www.instagram.com/explore/locations/" + str(LocationId) + "/" + str(text) + "/?__a=1")
                print("https://www.instagram.com/explore/locations/" +
                      str(LocationId) + "/" + str(text) + "/?__a=1")
            except Exception as e:
                print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
                time.sleep(60)
            else:
                if response and response.status_code != 200:
                    print("Request return " +
                          str(response.status_code) + " error!")
                    self.LastResponse = response
                    self.LastJson = json.loads(response.text)
                    return False
            finally:
                if response.status_code == 200:
                    def getMediaIdFromLocation(n):
                        return n['node']['id'], n['node']['owner']['id'], n['node']['comments_disabled']

                    self.LastResponse = response
                    print(len(json.loads(response.text)[
                        'graphql']['location']['edge_location_to_media']['edges']), "images found")
                    self.LastJson = list(map(getMediaIdFromLocation, json.loads(response.text)[
                        'graphql']['location']['edge_location_to_media']['edges']))
                    return list(set(self.LastJson))
        else:
            print("Request return " + str(response.status_code) + " error!")
            self.LastResponse = response
            self.LastJson = json.loads(response.text)
            return False

    def likeCommentFollowByLocation(self, text, like=False, follow=False, comment=False, thatComment=False,
                                    goToUserFeed=False, timeToSleep=False):
        posts = self.getPostsByLocation(text)
        likedCount = 0
        commenetsCount = 0
        visitCount = 0
        followCount = 0
        visitCommentsCount = 0
        visitLikedCount = 0
        thatComment = thatComment if thatComment else ["❤", "🤍", '🖤', '❤️']
        for i in posts:
            if self.listen():
                break
            if not (like or comment or follow):
                break
            if follow:
                if not self.api.follow(i[1]):
                    follow = False
                    print("follow blocked")
                else:
                    followCount += 1
                    self.users_i_follow.append((i[1], False))

            if self.did_i_comment(i[0]):
                print("allready comment")
                continue
            if like:
                if not self.api.like(i[0]):
                    print("like blocked")
                    if "message" in self.api.LastJson.keys() and self.api.LastJson[
                            'message'] == 'Sorry, this media has been deleted':
                        print("this media has been delete")
                    else:
                        like = False
                else:
                    likedCount += 1
            if comment and not i[2]:
                if not self.api.comment(i[0], random.choice(thatComment)):
                    print("comment blocked")
                    if "feedback_title" in self.api.LastJson.keys() and (
                            self.api.LastJson['feedback_title'] == 'Commenting is Off' or self.api.LastJson[
                                'feedback_title'] == "Couldn't Post Your Comment"):
                        print("Commenting on this post is Off or limit")
                    else:
                        comment = False
                else:
                    commenetsCount += 1
            if goToUserFeed and (like or comment):
                visit = self.doLikesToThisUser(
                    int(i[1]), False, comment, thatComment, doLike=like, timeToSleep=timeToSleep)
                if (visit[0] == False or visit[1] == False):
                    if visit[0] == False:
                        goToUserFeed = False
                    else:
                        visitLikedCount += visit[2]
                    if visit[1] == False:
                        comment = False
                    else:
                        visitCommentsCount += visit[3]
                else:
                    visitLikedCount += visit[2]
                    visitCommentsCount += visit[3]
                visitCount += 1
            print(" location post number", posts.index(i), end='\r')
            None if not timeToSleep or random.choice([True, False, False]) else time.sleep(
                random.randrange(timeToSleep))

        if not visitCount == 0:
            self.print_and_log("visit", visitCount, "users and liked", visitLikedCount,
                               "posts and comments", visitCommentsCount, "comments from visits")
        self.print_and_log("followed", followCount, "users, liked", likedCount,
                           "posts and comments", commenetsCount, "comments to the location posts")

    def sendToUsers(self, userIWantToStillFrom=None, getUserFollowings=True, text=None, mediaId=None,
                    last_massage_index=None, timeToSleep=False, likers=False):
        if (userIWantToStillFrom == None):
            userIWantToStillFrom = self.pkOf(self.userName)
        elif (type(userIWantToStillFrom) != int):
            self.api.searchUsername(userIWantToStillFrom)
            userIWantToStillFrom = self.api.LastJson['user']['pk']
        if (likers):
            self.api.getUserFeed(
                userIWantToStillFrom)  # Get user feed
            photoIndex = random.randrange(
                int(len(self.api.LastJson['items']) ** (1 / 3)))
            media_id = self.api.LastJson['items'][photoIndex]['id']
            self.api.getMediaLikers(media_id)
            users = list(map(self.getPk, self.api.LastJson['users']))
        elif (getUserFollowings):
            users = list(
                map(self.getPk, self.api.getTotalFollowings(userIWantToStillFrom)))
        else:
            users = list(
                map(self.getPk, self.api.getTotalFollowers(userIWantToStillFrom)))
        users = users[last_massage_index:] if last_massage_index != None else users
        messagesSned = 0
        for i in users:
            if not self.sendMassage(i[0], text, mediaId):
                print(messagesSned, "number of messages was send")
                self.res += str(messagesSned) + " number of messages was send"
                break
            messagesSned += 1
            print("send massage number", messagesSned, "to", i[1])
            None if not timeToSleep or random.choice([True, False, True, True]) else time.sleep(
                random.randrange(timeToSleep))
        return last_massage_index + messagesSned

    def sendMassage(self, userIWantToSendPk, text=None, mediaId=None, link=None):
        if text is not None:
            if type(text) is list:
                text = random.choice(text)
            text = text.encode('utf-8').decode('Latin-1')
        if mediaId is not None:
            res = self.api.direct_share(
                mediaId, userIWantToSendPk, text)
        elif link is not None:
            res = self.api.direct_link(link, userIWantToSendPk, text)
        else:
            res = self.api.direct_message(text, userIWantToSendPk)
        return res

    def getPkNoVerified(self, n):
        # if n["is_verified"] == True:
        #     print("can't unfollow user verified", n['username'])
        #     return
        if n["is_verified"] == False:
            return n["pk"], n['username'], n['is_private']
        else:
            print("can't unfollow user verified", n['username'])
        # return  n["pk"], n['username'], n['is_private'] if n["is_verified"] == False else None

    def getPk(self, n):
        return n["pk"], n['username'], n['is_private']

    def get_last_notification(self):
        suggested = [(n['user']['pk'], n['user']['username'], n['user']['is_private'])
                     for n in self.api.LastJson['aymf']['items']]
        self.api.LastJson['aymf'] = None
        pepoleLikedMe = []
        likedMe = []
        for i in self.api.LastJson['old_stories']:
            if i['type'] == 3:
                j = i['args']['inline_follow']['user_info']
                pepoleLikedMe.append((j['id'], j['username'], j['is_private']))
            if i['type'] == 1:
                j = i['args']
                likedMe.append(
                    (i['args']['profile_id'], i['args']['profile_name']))
        print("\n\nsuggested pepole: ", suggested)
        print("\n\npepole who liked me: ", list(set(likedMe)))
        print("\n\npepole who follow you: ", pepoleLikedMe)

    def random_feed(self, feed):
        length = len(feed)
        x = length ** (1 / 3)
        x = int((x + 5) / 2)
        feed = feed[:random.randrange(x) * x]
        random.shuffle(feed)
        feed = feed[: int(len(feed) / x)]
        return feed

    def getPostCommenters(self, mediaId, count=False, until_date=False):
        has_more_comments = True
        max_id = ''
        comments = []
        # TODO add sort by until_date
        # if until_date:
        #     import datetime
        if not self.canGetCommenters:
            return False
        try:
            while has_more_comments:
                self.api.getMediaComments(mediaId, max_id=max_id)
                # comments' page come from older to newer, lets preserve desc order in full list
                for c in reversed(self.api.LastJson['comments']):
                    c = (c['user']['pk'], c['user']['username'], c['user']['is_private'], c['pk']) if not until_date else (
                        c['user']['pk'], c['user']['username'], c['user']['is_private'], c['pk'], c['created_at_utc'])
                    comments.append(c)
                has_more_comments = self.api.LastJson.get(
                    'has_more_comments', False)
                # evaluate stop conditions
                if count and len(comments) >= count:
                    # comments = comments[:count]
                    # stop loop
                    has_more_comments = False
                    print("stopped by count return", len(comments), "comments")
                    break
                # if until_date:
                    # older_comment = comments[-1]
                # next page
                if has_more_comments:
                    max_id = self.api.LastJson.get('next_max_id', False)
                    time.sleep(2)
        except:
            self.print_and_log("can't get any more commenters")
            self.canGetCommenters = False
        else:
            return comments

    def did_i_comment(self, mediaId, returnCommenters=False, returnCommentPk=False):
        mediaId = str(mediaId)
        commenters = self.getPostCommenters(mediaId=mediaId)
        if not commenters:
            return False
        for i in commenters:
            if self.api.username_id == i[0]:
                if returnCommentPk:
                    return i[3], True
                if returnCommenters:
                    return commenters, True
                return True
        # else:
            # return False
        # print(commenters)
        if returnCommenters:
            return commenters, False
        return False

    def doLikesToThisUser(self, userIWantToLike, userName=False, doComment=False, thatComment=False, toLikeAll=False,
                          doLike=True, timeToSleep=False, no_duplicate_users=False, no_duplicate_comments=False, no_anonymous_profile=True):
        if (type(userIWantToLike) != int):
            pk = self.pkOf(userIWantToLike)
            if (pk == False):
                print("invalid pk the user name isn't found")
                self.res += "\nError: invalid pk the user name isn't found"
                return [False, False]
        else:
            pk = userIWantToLike
        if (self.login):
            api = self.api
            feed = False
            # response = False
            try:
                feed = api.getTotalUserFeed(pk)
            except:
                if not feed and 'message' in json.loads(self.api.LastResponse.text) and json.loads(self.api.LastResponse.text)['message'] == 'Not authorized to view user':
                    print("cant get feed",
                          userName if userName else "", "private user")
                    return [doLike, doComment, 0, 0]
                print("cant get feeed", userName if userName else "")
                return [False, False, 0, 0]
            else:
                if len(feed) == 0:
                    print(userName if userName else "",
                          "have no feed or user blocked me")
                    # self.res += str(userName) if userName else "" + " have no feed\n"
                    return [doLike, doComment, 0, 0]
                if feed and len(feed) > 0:
                    if no_anonymous_profile and feed[0]['user']['has_anonymous_profile_picture']:
                        print("can't like feed of anonymous profile")
                        return [doLike, doComment, 0, 0]
                    if (userName == False):
                        userName = feed[0]['user']['username']
                    # print(feed[0])
                    feed = [(i['pk'], i['comment_threading_enabled']) if 'comment_threading_enabled' in i else (
                        i['pk'], False) for i in feed]

                    feddLength = len(feed)
                    if doComment:
                        thatComment = thatComment if thatComment else [
                            "❤", "🤍", '🖤', '❤️']
                    commentCount = 0
                    likeCount = 0
                    if (toLikeAll):
                        i = 0
                        while i < feddLength:
                            if not doComment and not doLike:
                                break
                            if doComment and not self.did_i_comment(feed[i][0]):
                                if random.choice([True, False, False]) and feed[i][1]:
                                    if not api.comment(feed[i][0], random.choice(thatComment)):
                                        doComment = False
                                        commentCount -= 1
                                    commentCount += 1
                            if doLike:
                                if not api.like(feed[i][0]):
                                    doLike = False
                                    likeCount -= 1
                                i += 1
                                likeCount += 1
                        print("I liked", likeCount, "photos and commented",
                              commentCount, "comments to", userName)
                        self.res += "I liked " + \
                                    str(i) + " photos and commented " + \
                                    str(commentCount) + \
                                    " comments to " + userName + "\n"
                        return [doLike, doComment, likeCount, commentCount]
                    else:
                        if no_duplicate_users and userName in self.users:
                            return [doLike, doComment, likeCount, commentCount]
                        elif no_duplicate_users:
                            self.users.append(userName)
                        oldFeed = feed
                        feed = self.random_feed(feed)
                        if len(feed) == 0:
                            return [doLike, doComment, likeCount, commentCount]
                        feddLength = len(feed)
                        posts_i_like_and_comments = {"like": [], "comment": []}
                        for i in feed:
                            indexOfFeed = oldFeed.index(i) + 1
                            if not doLike and not doComment:
                                break
                            if doLike:
                                if not api.like(i[0]):
                                    print("likes to", userName,
                                          "was blocked on post number", indexOfFeed)
                                    if "message" in self.api.LastJson.keys() and self.api.LastJson[
                                            'message'] == 'Sorry, this media has been deleted':
                                        print("this media has been delete")
                                    else:
                                        doLike = False
                                    continue
                                likeCount += 1
                                posts_i_like_and_comments['like'].append(
                                    indexOfFeed)
                            if doComment and random.choice([True, False, doLike]) and i[1]:
                                if no_duplicate_comments and self.did_i_comment(i[0]):
                                    print("allready comments on post number",
                                          indexOfFeed, "of", userName)
                                    continue
                                commentText = random.choice(thatComment)
                                if not api.comment(i[0], commentText * (random.randrange(4) + 1) if len(
                                        commentText) == 1 else commentText):
                                    print("comments to", userName,
                                          "was blocked on post number", indexOfFeed)
                                    if "feedback_title" in self.api.LastJson.keys() and (
                                            self.api.LastJson['feedback_title'] == 'Commenting is Off' or
                                            self.api.LastJson['feedback_title'] == "Couldn't Post Your Comment"):
                                        print(
                                            "Commenting on this post is Off or limit")
                                    elif "message" in self.api.LastJson.keys() and self.api.LastJson[
                                            'message'] == 'Sorry, this media has been deleted':
                                        print("this media has been delete")
                                    else:
                                        doComment = False
                                    continue
                                commentCount += 1
                                posts_i_like_and_comments['comment'].append(
                                    indexOfFeed)
                            self.timeToSleep(timeToSleep=timeToSleep, randomList=[
                                             doComment, doLike, False])
                        print("I liked", likeCount, str("posts to posts number " + ','.join(
                            map(str, posts_i_like_and_comments['like']))) if likeCount > 0 else "posts",
                            str("and commented " + str(
                                commentCount) + " comments on posts number " + ','.join(
                                map(str, posts_i_like_and_comments['comment'])) + " to") if (
                            commentCount > 0) else "of", userName)
                        return [doLike, doComment, likeCount, commentCount]
                print("can't get", userName if userName else "", "feed")
                self.res = "can't get " + \
                           str(userName + " feed\n" if userName else "feed\n")
                print(userIWantToLike, userName)
        return [False, False, 0, 0]

    def getUserPk(self, text, confirm=False, needToBePublic=False):
        oldSelf = self
        self = self.api
        response = False
        try:
            response = self.s.get("https://www.instagram.com/web/search/topsearch/?context=blended&query=" +
                                  str(text) + "&rank_token=" + str(self.rank_token) + "&include_reel=true")
        except Exception as e:
            print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
            time.sleep(60)

        if response and response.status_code == 200:
            self.LastResponse = response
            self.LastJson = json.loads(response.text)
            if confirm:
                res = input("this is your user: '" + str(
                    self.LastJson['users'][0]['user']['username']) + "'\nyes to confirm\n")
                if res == "yes":
                    if not (self.LastJson['users'][0]['user']['is_private'] == False or needToBePublic):
                        return oldSelf.getUserPk(oldSelf, input("enter new user name\n"), True)
                    return (self.LastJson['users'][0]['user']['pk'], self.LastJson['users'][0]['user']['username'],
                            self.LastJson['users'][0]['user']['is_private'])
                res = input("do you what to try agin?\nyes to confirm\n")
                if res == "yes":
                    return oldSelf.getUserPk(oldSelf, input("enter new user name\n"), True)
                return False
            return (self.LastJson['users'][0]['user']['pk'], self.LastJson['users'][0]['user']['username'],
                    self.LastJson['users'][0]['user']['is_private'])
        else:
            print("Request return " + str(response.status_code) + " error!")
            self.LastResponse = response
            self.LastJson = json.loads(response.text)

    def Instafollow(self, is_verified=True, doLikes=False, doComments=False, thatComment=False, follow=True,
                    timeToSleep=False):
        followBack = not follow
        if (self.login):
            api = self.api
            # api.unblock(pkOf('mor_bargig'))
            if (is_verified == True):
                try:
                    Followings = list(
                        filter(None, map(self.getPkNoVerified, api.getTotalSelfFollowings())))
                    Followers = list(
                        filter(None, map(self.getPkNoVerified, api.getTotalSelfFollowers())))
                except KeyError:
                    print("Can't get user following or followers")
                    self.res += "Can't get user following or followers\n"
                    return
            else:
                try:
                    Followings = list(
                        map(self.getPk, api.getTotalSelfFollowings()))
                    Followers = list(
                        map(self.getPk, api.getTotalSelfFollowers()))
                except KeyError:
                    print("Can't get user following or followers")
                    self.res += "Can't get user following or followers\n"
                    return

            self.api.getSelfUsernameInfo()
            print("Progrem pull:\n", "Followings: ", len(
                Followings), "Followers: ", len(Followers))
            print("Instagram Profile count:\n", "Followings: ",
                  self.api.LastJson['user']['following_count'], "Followers: ", self.api.LastJson['user']['follower_count'])
            if not (0.9 < (len(Followings) / self.api.LastJson['user']['following_count']) < 1.1):
                print('user followings in profile data:',
                      self.api.LastJson['user']['following_count'], 'user followings pulling:', len(Followings))
                self.print_and_log(
                    "Can't continue with Instafollow because followers and following are False")
                return
            if not (0.9 < (len(Followers) / self.api.LastJson['user']['follower_count']) < 1.1):
                print('user followers in profile data:',
                      self.api.LastJson['user']['follower_count'], 'user followers pulling:', len(Followers))
                self.print_and_log(
                    "Can't continue with Instafollow because followers and following are False")
                return
            i = 0
            errorCount = 0
            unfollowUserCount = 0
            userILikeCount = 0
            likesIDo = 0
            commentsIDo = 0
            followBackUser = 0
            notFollowBack = list(set(Followings) - set(Followers))
            notFollowBackLength = len(notFollowBack)
            unfollow = True
            random.shuffle(notFollowBack)
            while errorCount < 2 and userILikeCount < 300 and i < notFollowBackLength and (
                    unfollow or doLikes or doComments):
                if i % 100 == 0:
                    print("Don't follow me back",
                          notFollowBackLength - userILikeCount)
                if self.listen():
                    break
                if doLikes or doComments:
                    visit = self.doLikesToThisUser(
                        notFollowBack[i][0], notFollowBack[i][1], doComments, thatComment, doLike=doLikes)
                    if (visit[0] == False or visit[1] == False):
                        if (visit[0] == False):
                            doLikes = False
                        else:
                            likesIDo += visit[2]
                        if (visit[1] == False):
                            doComments = False
                        else:
                            commentsIDo += visit[3]
                    else:
                        likesIDo += visit[2]
                        commentsIDo += visit[3]
                    userILikeCount += 1
                if unfollow:
                    if api.unfollow(notFollowBack[i][0]) == True:
                        unfollowUserCount += 1
                        print("unfollow number", unfollowUserCount,
                              "to", notFollowBack[i][1])
                    else:
                        print("can't unfollow",
                              notFollowBack[i][1], "unfollow blocked")
                        errorCount += 1
                        unfollow = False
                if unfollow and followBack:
                    if api.follow(notFollowBack[i][0]) == True:
                        followBackUser += 1
                        print("follow number", followBackUser,
                              "to", notFollowBack[i][1])
                    else:
                        print("can't follow",
                              notFollowBack[i][1], "follow blocked")
                        followBack = False
                i += 1
                print(" index", i, self.userName, end='\r')
                self.timeToSleep(timeToSleep=timeToSleep, randomList=[
                                 doComments, doLikes, unfollow, followBack])

            if (likesIDo != 0):
                print("unfollow", unfollowUserCount, "users likes",
                      likesIDo, "posts and commented", commentsIDo, "comments to", userILikeCount, "users")
                self.res += "unfollow " + str(unfollowUserCount) + " users  likes " + str(
                    likesIDo) + " posts and commented " + str(commentsIDo) + " comments to " + str(
                    userILikeCount) + " users"
            else:
                print("unfollow", unfollowUserCount, "users")
                self.res += "unfollow " + str(unfollowUserCount) + " users"
            if (followBackUser != 0):
                print("follow back to", followBackUser, "users")
                self.res += "follow back to " + str(followBackUser) + " users"

    def getUserFollowing(self, userIWantToLike, doLikes=False, doComments=False, thatComment=False, follow=True,
                         timeToSleep=False):
        if (self.login):
            if (type(userIWantToLike) != int):
                pk = self.pkOf(userIWantToLike)
                if (pk == False):
                    pk = self.getUserPk(
                        userIWantToLike, confirm=False, needToBePublic=True)  # confirm true
                    if not pk:
                        print("Error: invalid user name")
                        self.res += "Error: invalid user name"
                        return
                    print("get", pk[1], "following")
                    self.res += "get " + str(pk[1]) + " following\n"
                    pk = pk[0]
            else:
                pk = userIWantToLike
            api = self.api
            try:
                isFollowings = map(self.getPk, api.getTotalFollowings(pk))
                myFollowings = map(self.getPk, api.getTotalSelfFollowings())
                myFollowers = map(self.getPk, api.getTotalSelfFollowers())
            except KeyError:
                print("can't get followings")
                self.res += "can not get followings"
                return
            usersIWantToFollow = list(set(isFollowings) - set(myFollowings) - set(myFollowers) - {(self.pkOf(
                self.userName), self.userName, True)} - {(self.pkOf(self.userName), self.userName, False)})
            usersIWantToFollowLength = len(usersIWantToFollow)
            print(usersIWantToFollowLength, "users I want to follow")
            followedUser = 0
            i = 0
            userILikeCount = 0
            likesIDo = 0
            commentsIDo = 0
            while i < usersIWantToFollowLength and (follow or doLikes or doComments):
                if self.listen():
                    break
                if usersIWantToFollow[i]:
                    if follow:
                        if not api.follow(usersIWantToFollow[i][0]):
                            print("follow to",
                                  usersIWantToFollow[i][1], "was blocked")
                            follow = False
                        else:
                            followedUser += 1
                            print("follow number", followedUser,
                                  "to", usersIWantToFollow[i][1])
                    if not usersIWantToFollow[i][2] and (doLikes or doComments):
                        visit = self.doLikesToThisUser(
                            usersIWantToFollow[i][0], usersIWantToFollow[i][1], doComments, thatComment, doLike=doLikes)
                        if not visit[0] or not visit[1]:
                            if not visit[0]:
                                doLikes = False
                            else:
                                likesIDo += visit[2]
                            if not visit[1]:
                                doComments = False
                            else:
                                commentsIDo += visit[3]
                        else:
                            likesIDo += visit[2]
                            commentsIDo += visit[3]
                        userILikeCount += 1
                i += 1

                print(" index", i, self.userName, end='\r')
                None if not timeToSleep or random.choice([True, False]) else time.sleep(
                    random.randrange(timeToSleep))
            if (likesIDo != 0 or commentsIDo != 0):
                print("followed", followedUser, "users likes",
                      likesIDo, "posts and commented", commentsIDo, "comments to", userILikeCount, "users")
                self.res += "followed " + str(followedUser) + " users  likes " + str(
                    likesIDo) + " posts and commented " + str(commentsIDo) + " comments to " + str(
                    userILikeCount) + " users"
            else:
                print("followed", followedUser, "users")
                self.res += "followed " + str(followedUser) + " users"

    def getUserFollowers(self, userIWantToLike, doLikes=False, doComments=False, thatComment=False, timeToSleep=False,
                         follow=True):
        if (self.login):
            if (type(userIWantToLike) != int):
                pk = self.pkOf(userIWantToLike)
                if (pk == False):
                    while (True):
                        pk = self.getUserPk(
                            text=userIWantToLike, confirm=False)  # confirm true
                        if not pk:
                            print("Error: invalid user name")
                            self.res += "Error: invalid user name"
                            return
                        if pk[2]:
                            print("can't do, user",
                                  pk[1], "are private account")
                            self.res += "can't do, " + \
                                        str(pk[1]) + \
                                " user are private account\n"
                            confirm = input(
                                'do you like to enter new username\nusername to continue or "no" to cancel\n')
                            if confirm == "no":
                                return
                            userIWantToLike = confirm
                            continue
                        print("get", pk[1], "followers")
                        self.res += "get " + str(pk[1]) + " followers\n"
                        pk = pk[0]
                        break
            else:
                pk = userIWantToLike
            api = self.api
            myFollowings = map(self.getPk, api.getTotalSelfFollowings())
            myFollowers = map(self.getPk, api.getTotalSelfFollowers())
            isFollowings = map(self.getPk, api.getTotalFollowers(pk))
            usersIWantToFollow = list(set(isFollowings) - set(myFollowings) - set(myFollowers) - {(self.pkOf(
                self.userName), self.userName, True)} - {(self.pkOf(self.userName), self.userName, False)})
            usersIWantToFollowLength = len(usersIWantToFollow)
            print(usersIWantToFollowLength, "users I want to follow")
            followedUser = 0
            i = 0
            userILikeCount = 0
            likesIDo = 0
            commentsIDo = 0
            while (follow or doLikes or doComments) and i < usersIWantToFollowLength:
                if self.listen():
                    break
                if usersIWantToFollow[i]:
                    if follow:
                        if not api.follow(usersIWantToFollow[i][0]):
                            print("follow to",
                                  usersIWantToFollow[i][1], "was blocked")
                            follow = False
                        else:
                            followedUser += 1
                            print("follow number", followedUser,
                                  "to", usersIWantToFollow[i][1])
                    if not usersIWantToFollow[i][2] and (doLikes or doComments):
                        visit = self.doLikesToThisUser(
                            usersIWantToFollow[i][0], usersIWantToFollow[i][1], doComments, thatComment, doLike=doLikes)
                        if not visit[0] or not visit[1]:
                            if not visit[0]:
                                doLikes = False
                            else:
                                likesIDo += visit[2]
                            if not visit[1]:
                                doComments = False
                            else:
                                commentsIDo += visit[3]
                        else:
                            likesIDo += visit[2]
                            commentsIDo += visit[3]
                        userILikeCount += 1
                i += 1
                print(" index", i, self.userName, end='\r')
                None if not timeToSleep or random.choice([True, False]) else time.sleep(
                    random.randrange(timeToSleep))
            if (likesIDo != 0):
                print("followed", followedUser, "users likes",
                      likesIDo, "posts and commented", commentsIDo, "comments to", userILikeCount, "users")
                self.res += "followed " + str(followedUser) + " users  likes " + str(
                    likesIDo) + " posts and commented " + str(commentsIDo) + " comments to " + str(
                    userILikeCount) + " users"
            else:
                print("followed", followedUser, "users")
                self.res += "followed " + str(followedUser) + " users"

    def get_all_about_user(self, isFollowers=True, self_or_pk=True, userName=False):
        if not self.login:
            return
        Snapchat = []
        data = ''
        usersData = {}
        keyList = ['category', 'contact_phone_number', 'public_email',
                   'public_phone_number', 'city_name', 'is_business', 'pk', 'username', 'is_private',
                   'has_anonymous_profile_picture', 'is_verified', 'media_count', 'follower_count', 'following_count']
        if userName:
            self.api.searchUsername(userName)
            print(self.api.LastJson)
            i = self.api.LastJson['user']
            print((i['media_count'], i['follower_count'], i['following_count']))
            for i in keyList:
                if i in self.api.LastJson['user']:
                    if self.api.LastJson['user'][i] != '':
                        data += i + ": " + \
                            str(self.api.LastJson['user'][i]) + '\n'
            print(data)
            return

        if self_or_pk and isinstance(self_or_pk, int):
            if isFollowers:
                users = [(n["pk"], n['username'], n['is_private'])
                         for n in self.api.getTotalFollowers(self_or_pk)]
            else:
                users = [(n["pk"], n['username'], n['is_private'])
                         for n in self.api.getTotalFollowings(self_or_pk)]
        elif self_or_pk:
            if isFollowers:
                users = [(n["pk"], n['username'], n['is_private'])
                         for n in self.api.getTotalSelfFollowers()]
            else:
                users = [(n["pk"], n['username'], n['is_private'])
                         for n in self.api.getTotalSelfFollowings()]
        elif not self_or_pk:
            print(
                "error must have user pk or defult self follower or following to start colacting data")
            return
        for user in users:
            print(user)
            if not self.api.searchUsername(user[1]):
                print("can't get user info of", user[1])
                break
            string = str(self.api.LastJson['user']['biography'])
            SnapchatList = ['Snapchat', 'snapchat', 'Snap', 'snap', '�👻']
            TikTokList = ['TikTok', 'Tiktok']
            FacebookList = ['Facebook', 'facebook']
            emailList = ['Email', 'email']
            mediaLists = [SnapchatList, emailList, FacebookList, TikTokList]
            hasData = False
            for mediaList in mediaLists:
                for i in mediaList:
                    if i in string:
                        M_U_N = False
                        try:
                            M_U_N = ((string[string.find(i): string.find(
                                i) + len(i) + 20]).split(':')[1]).split(' ')
                        except IndexError:
                            M_U_N = ((string[string.find(i): string.find(
                                i) + len(i) + 20]).split('-')[1]).split(' ')
                        index = 0
                        while (M_U_N[index] == ''):
                            index += 1
                        if mediaList == FacebookList:
                            M_U_N = M_U_N[index] + ' ' + \
                                M_U_N[index + 1].split('\n')[0]
                        else:
                            M_U_N = M_U_N[index]
                            M_U_N = M_U_N.split(",")[0]
                            M_U_N = M_U_N.split("'")[0]
                            M_U_N = M_U_N.split('\n')[0]
                        print(user[1], str(mediaList[0]) + ":", M_U_N)
                        self.res += str(mediaList[0]) + \
                            ' of' + str(user[1]) + M_U_N + '\n'
                        Snapchat.append(
                            (user[0], user[1], mediaList[0], M_U_N))
                        if not hasData:
                            data += user[1] + ": \n"
                            usersData[user[1]] = {}
                            usersData[user[1]
                                      ]['full_name'] = self.api.LastJson['user']['full_name']
                            hasData = True
                        usersData[user[1]][mediaList[0]] = M_U_N
                        data += '\t\t' + str(mediaList[0]) + ":" + M_U_N + '\n'
                        break
            for i in keyList:
                if i in self.api.LastJson['user']:
                    if self.api.LastJson['user'][i] != '' and self.api.LastJson['user'][i] != None and \
                            self.api.LastJson['user'][i] != False:
                        if not hasData:
                            data += user[1] + ": \n"
                            usersData[user[1]] = {}
                            hasData = True
                            usersData[user[1]
                                      ]['full_name'] = self.api.LastJson['user']['full_name']
                            data += "\t\tfull_name: " + \
                                    self.api.LastJson['user']['full_name'] + '\n'
                        data += '\t\t' + i + ": " + \
                                str(self.api.LastJson['user'][i]) + '\n'
                        usersData[user[1]][i] = self.api.LastJson['user'][i]
            match = re.search(r'[\w\.-]+@[\w\.-]+', string)
            if match != None:
                data += '\t\t' + \
                        str(emailList[0]) + ":" + match.group(0) + '\n'
                usersData[user[1]][emailList[0]] = match.group(0)
                print(user[1], str(emailList[0]) + ":", match.group(0))
                self.res += user[1] + str(emailList[0]) + \
                    ":" + str(match.group(0)) + '\n'
        print(Snapchat, '\nget', len(list(usersData)),
              "users data\n", data, '\n', usersData)
        self.res += 'get ' + str(len(list(usersData))) + " users data\n"
        return usersData

    def like_feed(self, none, like=True, comment=True, thatComment=False, follow=False, goToUserFeed=False, timeToSleep=False):
        self.api.getPopularFeed()
        like = True
        comments = thatComment
        if not comments:
            comment = False
        likeCount = 0
        postCount = 0
        commentsCount = 0
        visitLikedCount = 0
        visitCommentsCount = 0
        followCount = 0
        visitCount = 0
        feed = [(i['pk'], i['comment_threading_enabled'], i['user']['pk'], i['user']['username'])
                if 'comment_threading_enabled' in i else (i['pk'], False, i['user']['pk'], i['user']['username']) for i in self.api.LastJson['items']]
        for i in feed:
            if self.listen():
                break
            if not (like or comment or follow):
                break
            if follow:
                if not self.api.follow(i[2]):
                    print("follow blocked to", i[3])
                    follow = False
                    continue
                followCount += 1
                self.users_i_follow.append((i[2], i[3]))
                print("follow number", followCount, "to", i[3])
            if like:
                if not self.api.like(i[0]):
                    print("liked blocked")
                    if "message" in self.api.LastJson.keys() and self.api.LastJson[
                            'message'] == 'Sorry, this media has been deleted':
                        print("this media has been delete")
                    else:
                        like = False
                likeCount += 1
            if comment and random.choice([True, False]) and i[1] and not self.did_i_comment(i[0]):
                if not self.api.comment(i[0], random.choice(comments)):
                    print('comments blocked')
                    if self.api.LastJson and "feedback_title" in self.api.LastJson.keys() and (
                            self.api.LastJson['feedback_title'] == 'Commenting is Off' or self.api.LastJson[
                                'feedback_title'] == "Couldn't Post Your Comment"):
                        print("Commenting on this post is Off or limit")
                    else:
                        comment = False
                commentsCount += 1
            if goToUserFeed and (like or comment):
                visit = self.doLikesToThisUser(
                    int(i[2]), i[3], doComment=comment and i[1], thatComment=thatComment, doLike=like, timeToSleep=timeToSleep)
                if (visit[0] == False or visit[1] == False):
                    if visit[0] == False:
                        goToUserFeed = False
                    else:
                        visitLikedCount += visit[2]
                    if visit[1] == False:
                        comment = False
                    else:
                        visitCommentsCount += visit[3]
                else:
                    visitLikedCount += visit[2]
                    visitCommentsCount += visit[3]
                visitCount += 1
            postCount += 1
            print(" post number", feed.index(i), "of", i[3], end='\r')
            None if not timeToSleep else time.sleep(
                random.randrange(timeToSleep))
        if visitCount > 0:
            self.print_and_log("visit", visitCount, "users and liked", visitLikedCount,
                               "posts and comments", visitCommentsCount, "comments from visits")
        self.print_and_log("likes", likeCount, "posts and commented",
                           commentsCount, "comments to", postCount, "post")
