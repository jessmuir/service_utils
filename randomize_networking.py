"""
Generate randomized networking groups, with mix of junior and senior people
For variable participant numbers, group sizes
output CSV file
"""

import numpy as np


#==================================================================
def gen_groups(rsvpdict,order,Nblocks=4,groupsize=4):
    """
    arrange people into groups of groupsize people
    with Nblocks different groupings (time blocks for networking)
    
    -1's correspond to empty spots
    """
    total = 0
    otherkeys = []
    # count total rsvps, check for keys not in order
    for k in rsvpdict.keys():
        total+=rsvpdict[k]
        if k not in order:
            otherkeys.append(k)


    # each participant gets an id
    participant_list = []
    masks = {}
    for k in order:
        m = np.zeros(total,dtype=bool)
        m[len(participant_list):len(participant_list)+rsvpdict[k]]=True
        participant_list = participant_list+[k]*rsvpdict[k]
        masks[k]=m
        


    # one row per participant, columns are table numbers
    locs = -1*np.ones((total,Nblocks),dtype=int) 
    
    
    remainder = total%groupsize
    Ngroup = total//groupsize
    if remainder:
        chairs = groupsize+1
    else:
        chairs= groupsize
    tables = -1*np.ones((Ngroup*Nblocks,chairs+2),dtype=int)
    # 2d array, first column is the time block, rows are table, columns are chairs
    blocklabels = np.repeat(np.arange(1,Nblocks+1),Ngroup)
    print("Ngroup",Ngroup,"Nblocks",Nblocks)
   
    tablelabels = np.tile(np.arange(1,Ngroup+1),Nblocks)
    tables[:,0] =blocklabels
    tables[:,1] = tablelabels
    

    tableinds = np.arange(1,Ngroup+1)
    pinds = np.arange(total) # array of participant indices
    for b in range(Nblocks):
        #print('unscrambled',np.arange(1,Ngroup+1))
        #np.random.shuffle(tableinds)        
        #np.random.shuffle(pinds)
        for cat in order: # shuffle order within each participant type
            catinds = pinds[masks[cat]]
            np.random.shuffle(catinds)
            pinds[masks[cat]]=catinds
            print('block',b,cat,catinds)
        locs[:,b]=np.tile(tableinds,chairs)[pinds]
        # now translate that info into who is seated at each table
        for t in range(1,Ngroup+1): # loop through table numbers
            tlist = np.where(locs[:,b]==t)[0] # indices of people at table t
            tables[b*Ngroup + t-1,2:2+tlist.size] = tlist
            
    return participant_list, locs, tables

def save_groups(participant_list, locs, tables,outnamebase):
    peoplefile=outnamebase+'_people.csv'
    tablefile=outnamebase+'_tables.csv'

    rows = np.array(participant_list,dtype='20U')[:,np.newaxis]
    ids = np.arange(1,locs.shape[0]+1)[:,np.newaxis]
    Nblocks = tables[:,0].max()
    chairs = tables.shape[1]-2
    with open(peoplefile,'w') as f:
        print("Saving participant locations to",peoplefile)
        header = 'id, type, '+''.join([str(b)+', ' for b in range(1,Nblocks+1)])
        np.savetxt(f,np.hstack((ids,rows,locs)),delimiter=', ',fmt='%s',header=header)

    with open(tablefile,'w') as f:
        print("Saving table info to",tablefile)
        header = "timeblock, table, "+''.join([str(c)+', ' for c in range(1,chairs+1)])
        rowinfo=[]
        for r in range(tables.shape[0]):
            cinfo=[]
            for c in range(chairs):
                if tables[r,2+c]==-1:
                    cinfo.append('empty')
                else:
                    cinfo.append(participant_list[tables[r,2+c]])
            rowinfo.append(cinfo)
        rowinfo = np.array(rowinfo,dtype='20U')
            
        np.savetxt(f,np.hstack((tables,rowinfo)),delimiter=', ',fmt='%s',header=header)

        
def group_rsvps(granular_rsvps,categories):
    newrsvps = {}
    # beware, not checking for "other"
    for cat in categories:
        count=0
        for subtype in categories[cat]:
            count+=granular_rsvps[subtype]
        newrsvps[cat]=count
    return newrsvps
            



#==================================================================
def main():
    #order= ['faculty','staff','postdoc','grad2+','grad12','psi']
    # including undergrad in psi
    rsvps = {
        'faculty':2,
        'staff':6,
        'postdoc':7,
        'grad2+':2,
        'grad12':6,
        'psi':10,
    }
    # group into some larger categories
    cats = {
        'senior':['faculty','staff'],\
        'postdoc':['postdoc'],\
        'phd':['grad2+','grad12'],
        'psi':['psi']
        }
    gr_rsvps=group_rsvps(rsvps,cats)
    order=['senior','postdoc','phd','psi']

    outname='test'
    Nblocks=4
    groupsize=4
    plist,locs,tables = gen_groups(gr_rsvps,order,Nblocks,groupsize)
    save_groups(plist,locs,tables,outname)
    

    # to do: simplify labels for output; e.g. group all grad students

#==================================================================
if __name__=="__main__":
    main()


