import re
import sys
import csv

def parse_file(filename):

    first = '<<< Wire List >>>'

    file = open(filename, 'r')

    res = []

    skipping = True

    for i, line in enumerate(file):
        if first in line:
            skipping = False

        if not skipping:
            res.append(line)

    assert not skipping

    return res

##! Breaks a space separated line into it's 5 parts
def break_line(line):
    m = re.search(' *([^ ]*) *([^ ]*) *([^ ]*) *([^ ]*) *([^ ]*)', line)

    res = []

    for i in range(1,6):
         res.append(m.group(i).rstrip().lstrip())

    return res


##! Takes all lines in the netlist file
# Breaks into a list where the first element is the header name
# and the next element is a list of lines that have been parsed
def parse_sections(lines):
    # print "got", len(lines), "lines"


    output = []

    last_header = None
    cur_lines = []


    for i, line in enumerate(lines):

        # if we have a section
        if line.startswith('['):

            # if we are starting a new section
            if last_header is not None:
                # Save output section
                output.append([last_header, cur_lines])

                # Reset to initial conditions
                last_header = None
                cur_lines = []


            # search for ] followed by a space and grab everything after that
            m = re.search('] (.*)', line)

            last_header = m.group(1).rstrip()
        else:
            # if we are under a header
            if last_header is not None:
                # If the line isn't blank
                if line.rstrip() != '':
                    # Add it
                    cur_lines.append(break_line(line))

    # The loop above will skip the final section, so grab it here
    if last_header is not None:
        # Save output section
        output.append([last_header, cur_lines])


    return output



def run_main(argv):

    argc = len(argv)
    designatorc = argc - 3
	
    filename = argv[1] #'170518-1_copper_suicide.net'
    netname = argv[2] #'U1B'
    harness_name = argv[3]

    secondary_nets = []

    for i in range(4,argc):
        #print ("range", i, argv[i])
        secondary_nets.append(argv[i])
    #print ("\n\n\n")

    #print (secondary_nets)

    # Make header line

    # This is repeated for every primary and secondary net
    csv_header_og = ['REFERENCE', 'PIN #', 'PIN NAME', 'PIN TYPE', 'PART VALUE']
    csv_header = list(csv_header_og)

    for net in secondary_nets:
        for hdr in csv_header_og:
            hdr_name = net + ' ' + hdr
            csv_header.append(hdr_name)
            #print csv_header

    # Add the first csv header
    csv_header_final = ['NET']
    # Add the rest
    csv_header_final.extend(csv_header)

    #print (','.join(csv_header_final))


    res = parse_file(filename)
    sections = parse_sections(res)

    length =len(sections)
    trace_names=[]
    subconnects=[]
    FPGA_Ball_Names=[]
    SDRAM_Pin_Names=[]
    SDRAM_Pin_Numbers=[]
    
    for i in range(0,length):
        if harness_name in sections[i][0]:
            print (sections[i])
            trace_names.append(sections[i][0])
            subconnects.append(sections[i][1])
    
    print (subconnects)
    print (trace_names)
    
    y=len(trace_names)
    for z in range(0,y):
        if harness_name+'SDR.' in trace_names[z]:
            FPGA_Ball_Names.append(subconnects[z][1][1])
            SDRAM_Pin_Names.append(subconnects[z][2][2])
            SDRAM_Pin_Numbers.append(subconnects[z][2][1])

        if harness_name+'DDR.' in trace_names[z]:
            FPGA_Ball_Names.append(subconnects[z][0][1])
            SDRAM_Pin_Names.append(subconnects[z][1][2])
            SDRAM_Pin_Numbers.append(subconnects[z][1][1])

        if '.D4_N' in trace_names[z]:
            FPGA_Ball_Names[z]=subconnects[z][1][1]
            SDRAM_Pin_Names[z]=subconnects[z][2][2]
            SDRAM_Pin_Numbers[z]=subconnects[z][2][1]
            
    result=[]
    for z in range (0,y):
        result.append(str(trace_names[z]) + ',' + str(FPGA_Ball_Names[z]) + ',' + str(SDRAM_Pin_Names[z]) + ',' + str(SDRAM_Pin_Numbers[z]))
        print (result[z].split(","))

    fp=open("test.txt","w")
    fp.write('Trace_Name' + ',' + 'FPGA_Ball_Names' + ',' + 'SDRAM_Pin_Names' + ',' + 'SDRAM_Pin_Numbers' + '\n')
    for z in range (0,y):
        fp.write(result[z])
        fp.write('\n')
    fp.close()

    with open('test.csv','w',newline='') as csvfile:
        file_write=csv.writer(csvfile,delimiter=',')
        file_write.writerow(['Trace_Name','FPGA_Ball_Names','SDRAM_Pin_Names','SDRAM_Pin_Numbers'])
        for z in range(0,y):
            file_write.writerow(result[z].split(","))

    secondary_line = []

    # Build a list which will hold the csv values for the secondary nets
    for i in range(len(secondary_nets)):
        for k in range(5):
            secondary_line.append('')

    for section in sections:
        header = section[0]
        nets = section[1]

        this_secondary_line = list(secondary_line)

        # Search for secondary nets first
        for row in nets:
            for k, secondary in enumerate(secondary_nets):

                # If we get a match
                if row[0] == secondary:
                    # print "secondary match"
                    # populate the secondary match line at the correct offset
                    this_secondary_line[k*5:(k+1)*5] = row
                    pass

        # At this point secondary nets will be filled out

        # print "###########", header
        for row in nets:
            # If this row matches the primary net
            if row[0] == netname:
                print (header + ',' + ','.join(row) + ',' + ','.join(this_secondary_line))


    pass

if __name__ == "__main__":
    run_main(sys.argv)
