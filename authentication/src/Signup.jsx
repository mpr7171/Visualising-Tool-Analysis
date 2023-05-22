import React from 'react';
import { auth } from "./firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { useState } from "react"; //importing useState hook to save changes
import validator from "validator"; // Importing the validator library

const Signup=()=> {
// year,branch,rollno,mahindra or not 
    const[name,setName]= useState("");
    const[email,setEmail]= useState(""); //initial value setEmail is empty String 
    const[password,setPassword]=useState("");
    const[confirmPassword,setConfirmPassword]=useState("");

    

    const extraction = (email) => {
        const year = email.match(/\d{2}/)[0];
        let branch=email.match(/\d+(.*?)\d+/)[1];
        
        //extracting roll no and its different formats for us and juniors hence handling that
        let rollNo;
        let se;
        if(year==='20'){
            se = email.replace(/^(.*?)20/, 'se20');
            rollNo = se.match(/^[^@]+/)[0];
        }
        else{
            rollNo=email.match(/^[^@]+/)[0];
        }

        //setting the branch
        if(branch==="uari"){
            branch="AI";
        }
        else if(branch==='ucse'){
            branch="CSE";
        }
        else if(branch==='uece'){
            branch="ECE";
        }
        else if(branch==='umee'){
            branch="ME";
        }
        else if(branch==='ueee'){
            branch="EEE";
        }
        else{
            branch="other";
        }

        return {year,branch,rollNo};
      };

    const handleSubmit=(event)=> {
        event.preventDefault(); //stops the submit from submitting and takes the values required 
        try{
            if(password===confirmPassword){
                if (validator.isEmail(email) && email.endsWith("mahindrauniversity.edu.in")) {
                    createUserWithEmailAndPassword(auth, email, password)
                    console.log("User signed up successfully");
                    const {year,branch,rollNo} = extraction(email);
                    console.log("Year of Joining:", year);
                    console.log("Branch",branch);
                    console.log("RollNo",rollNo);
                }
                else{
                    console.log("Only Mahindra Domain emails allowed");
                }
            }
            else{
                console.log("Passwords didnt match");//add css to show 
            }
        }
        catch(error){
            console.error("Error signing up:", error);
        }
    }

  return (
    <div>
      <h1>Sign Up</h1>
      <form onSubmit={handleSubmit}>
      {/* once the button is clicked with the form this function is called */}
      <div>
          <label>Name:</label>
          <input
            type="text"
            name="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
        </div>
        <div>
          <label >Email:</label>
          <input
            type="email"
            name="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>

        {/* <div>
        <label>Branch:</label>
        <input
          type="text"
          name="branch"
          value={branch}
          onChange={(event) => setBranch(event.target.value)}
        />
      </div> */}

        <div>
          <label>Semester:</label>
          <select name="Semester"> 
            <option value="1">1</option> 
            <option value="2">2</option> 
            <option value="3">3</option> 
            <option value="4">4</option> 
            <option value="5">5</option> 
            <option value="6">6</option> 
            <option value="7">7</option> 
            <option value="8">8</option> 
            </select>
        </div>

        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>

        <div>
          <label>Confirm Password:</label>
          <input
            type="password"
            name="confirmPassword"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            required
          />
        </div>

        <button type="submit">Sign Up</button>
      </form>
    </div>
  )
}

export default Signup;

