http://www.assembla.com/code/datatables_demo/subversion/nodes/trunk/1_6_2/datatables_demo?rev=2


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
