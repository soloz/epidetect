
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
 
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import au.com.bytecode.opencsv.CSVReader;
import au.com.bytecode.opencsv.CSVWriter;


public class Cruncher {

	public Cruncher(){
		
	}
	
	public void crunchJson() throws IOException {
		
		FileWriter file = null;
        JSONParser parser = new JSONParser();
        
        File directory = new File("data/input");
        int dirlength = directory.list().length;
        
        for (int i = 1; i<= dirlength ;i++){
        	
        try {
        	//System.out.println("data/output/000"+i+".json");
        	file = new FileWriter("data/output/"+i+".json");
        	
            Object inputobjs = parser.parse(new FileReader("data/input/"+i+".json"));
            
            //Input Array
            JSONArray inputArrays = (JSONArray) inputobjs;
            
            //Output Array
            JSONArray output_en = new JSONArray();
            
            //Setting the size of input array of json objects
            int sizing = inputArrays.size() ;
         		
          for (int j = 0; j<sizing ;j++){
        	  
        	  JSONObject obj = (JSONObject) inputArrays.get(j);
        	  String lang = (String) obj.get("lang");
        	  String eng = new String("en");
        	  
        	  if (lang != null)
	        	  if (lang.equals(eng)){
	        		  output_en.add(obj);
	        	  }
             //System.out.println("Language is "+lang+"for object "+i);
        
          }
          
            file.write(output_en.toJSONString());
            System.out.println("Successfully Copied JSON Array to File...");
            //System.out.println("\nJSON Array: " + output_en);
        
        } catch (Exception e) {
            e.printStackTrace();
        }finally {
            file.flush();
            file.close();
        }
        }
	}
	
		public void generateCSV() throws IOException{

			Pattern p = Pattern.compile("\\b(Influenza|flu|Coronavirus|Avian|Measles|Enterovirus|HFM|Dengue|Plague|Hendra|Swine|Hantavirus|SARS|Rotavirus|Cholera|Rabies|H1n1|Influenzavirus)\\b", Pattern.CASE_INSENSITIVE);
			Matcher m = null; 
			
			// create a CSVWriter reading from the file with the given name
	        String filename = "source.csv";
			JSONParser parser = new JSONParser();
			ArrayList<String[]> content = content = new ArrayList<String[]>();;
			
			if (new File("source.csv").exists()){
				
				System.out.println("File, "+filename+", exists");
				
				FileReader fr = new FileReader(filename);
				CSVReader reader = new CSVReader(fr);
			
				// read each line
				String[] nextLine = reader.readNext();
				
			    while ((nextLine = reader.readNext()) != null) {
			    		content.add(nextLine);
			    }
			    
			}
			
			FileWriter fw = new FileWriter(filename);
			CSVWriter writer = new CSVWriter(fw);
			
			 File directory = new File("data/output");
		     int dirlength = directory.list().length;
		 	  
		     
		     for (int i = 1; i<= dirlength ;i++){
		     
             try {
                	Object inputobjs = parser.parse(new FileReader("data/output/"+i+".json"));
        	        
                    //Input Array
                    JSONArray inputArrays = (JSONArray) inputobjs;
                	
                    //Setting the size of input array of json objects
                    int sizing = inputArrays.size() ;
                    
                    System.out.println(sizing);
                    
                    for (int j = 0; j<sizing ;j++){
                  	  
                  	 JSONObject obj = (JSONObject) inputArrays.get(j);
                  	  
                  	String text = (String) obj.get("text");
                  	m = p.matcher(text);
                  	
    	        	  if (m.find()){
    	        		  
                         String id = (String) obj.get("id_str");
                         String created_at = (String) obj.get("created_at");
                         String user = (String) obj.get("screen_name");
                         String location = (String) obj.get("location");
                         String coordinates = (String) obj.get("coordinates");
                         
                          String [] record = {id, user, text, location, coordinates, created_at};
                          
                          //val.put("text", name);
                          
                          content.add(record);
    	        	  }
    	         	
                    }
                    
                    writer.writeAll(content);
                                       
                                   
                } catch (Exception e) {
                    e.printStackTrace();
                }
       
		     }
		}
		
		
	    public static void main(String[] args) throws IOException {
	    	
	    	Cruncher cruncher = new Cruncher();
	    	//cruncher.crunchJson();
	    	
	    	cruncher.generateCSV();
	        
	    }
	    
	}