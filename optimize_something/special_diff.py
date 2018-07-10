import sys

def read_lines(filename):
 with open(filename) as f:
  lines = f.readlines()
 return lines

def spot_difference(debug_info):
 i,line1,line2=debug_info
 print 'DIFFERENCE IN LINE #{}:'.format(i)
 print line1
 print line2

def similar(x1,x2):
 return abs(x1-x2)<1e-6

def string_to_float(string):
 try:
  return float(string)
 except ValueError:
  return None

digits=[str(digit) for digit in range(10)]

def find_first_digit(string):
 n=len(string)
 for i in range(n):
  if string[i] in digits: return i
 return None

def find_last_digit(string):
 n=len(string)
 for i in range(n-1,-1,-1):
  if string[i] in digits: return i
 return None

def find_numbers_in_string(string):
 i0=find_first_digit(string)
 i1=find_last_digit(string)
 if i0==None or i1==None: return None
 return string[i0:i1+1]

def strings_to_numbers(strings):
 numbers=[]
 for string in strings:
  number=string_to_float(string)
  if number==None: 
   return None
  else:
   numbers.append(number)
 return numbers

def process_array(debug_info,numbers1,numbers2):
 n1=strings_to_numbers(numbers1.split())
 n2=strings_to_numbers(numbers2.split())
 if n1==None or n2==None or len(n1)!=len(n2):
  spot_difference(debug_info)
 else:
  n=len(n1)
  for i in range(n):
   if not similar(n1[i],n2[i]):
    spot_difference(debug_info)

def process_different_lines(debug_info):
 i,line1,line2=debug_info
 if line1==line2: return
 numbers1=find_numbers_in_string(line1)
 numbers2=find_numbers_in_string(line2)
 if numbers1==None or numbers2==None:
  spot_difference(debug_info)
  return
 process_array(debug_info,numbers1,numbers2)

def special_diff(lines1,lines2):
 if len(lines1)!=len(lines2):
  print 'THE NUMBER OF LINES IN BOTH FILES DOES NOT COINCIDE.'
  return
 n=len(lines1)
 for i in range(n):
  if lines1[i]!=lines2[i]:
   process_different_lines((i,lines1[i][:-1],lines2[i][:-1]))

def main():
 lines1=read_lines(sys.argv[1])
 lines2=read_lines(sys.argv[2])
 special_diff(lines1,lines2)

if __name__ == "__main__": main()
