import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json'
  })
}

@Injectable({
  providedIn: 'root'
})
export class SharedService {

  baseUrl: string = "";

  constructor(private http: HttpClient) { 
    this.baseUrl = environment.baseUrl;
  }

  uploadFile(fileType: string, file: File){
    const formData = new FormData();
    formData.append(fileType, file);

    if(fileType === "text-file"){
      return this.http.post(`${this.baseUrl}/api/corpus`, formData);
    }
    if(fileType === "resume-file"){
      return this.http.post(`${this.baseUrl}/api/acronyms`, formData);
    }
    return null;
  }

  getAllAcronyms(){
    return this.http.get(`${this.baseUrl}/api/acronyms`, httpOptions);
  }

  getAcronymFullForm(acronym){
    return this.http.get(`${this.baseUrl}/api/acronymFullForm/${acronym}`, httpOptions);
  }

}
