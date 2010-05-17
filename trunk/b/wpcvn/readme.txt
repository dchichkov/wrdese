Performance: http://lsimons.wordpress.com/2009/03/15/getting-a-feel-for-the-performance-of-mod_wsgi/



LOG RAW SOURCE DATA, NOT SOME POST PROCESSED JUNK
1) log irc feed
2) log user actions

IRC FEED --> filter(user_reputation < N) - add, mark unsafe (expiration) -> memcashed(page_id, change)
IRC FEED --> filter(user_reputation > N) - existing, mark good (expiration) -> memcashed(page_id, change)
                                
Web User --> verify account (ask to modify own user page & enter GUID in a comment)-> encrypted cookie (storing username)
Web User --> click on a diff -> memcashed(page_id, page views)
Web User --> mark as regular, vandalism, dunno (+types of vandalism) -> memcashed(page_id, safe)


UI: viewed - display glasses
    normal - black
    marked good - green & dissapear from view
    edited by a user with good reputation - update comment, mark green/gray, dissapear 

    marked dunno - display question makr
    marked bad - red & stay

Feed/update strings & expiration time. Always feed complete records.


AUTH:
Priority:
 wid - use if available
 nick - use if available

http://en.wikipedia.org/w/index.php?title=Wikipedia:Sandbox&action=edit&minor=true&section=0&summary=4AB96246-AC5F-65E0-EE6B-701A45A83141


 User requests auth: 
   USER: GUID, ip    ---> {GUID : (ip, '')}
   IRC: (GUID, user) ---> {GUID : (ip, user)}
   USER: GUID, ip    ---> 
                     <--- user, encrypted user
   USER: store encrypted user to cookie
   
 After that USER always uses encrypted cookie to authentify
 


