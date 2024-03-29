package com.mcc_project_5.Tools

import android.content.Context
import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.*
import okhttp3.RequestBody
import org.json.JSONObject
import com.google.firebase.auth.GetTokenResult
import com.google.android.gms.tasks.OnCompleteListener
import com.google.android.gms.tasks.Task
import java.io.File


class Requester(context: Context) {
    private val client = OkHttpClient()
    private val baseUrl = Properties(context).getProperty("baseUrl")
    val JSON = "application/json; charset=utf-8".toMediaType()
    private val X_FIREBASE_TOKEN = "Firebase-token"

    fun httpGetNoToken(url: String, callBack: Callback) {
        val request = Request.Builder()
            .url(baseUrl + url)
            .get()
            .build()

        val call = client.newCall(request)
        call.enqueue(callBack)
    }

    fun httpGet(url: String, callBack: Callback) {
        val mUser = FirebaseAuth.getInstance().currentUser ?: return
        mUser!!.getIdToken(true)
            .addOnCompleteListener(object : OnCompleteListener<GetTokenResult> {
                override fun onComplete(task: Task<GetTokenResult>) {
                    if (task.isSuccessful()) {
                        val idToken = task.getResult()?.getToken()
                        Log.d("token", idToken)
                        val request = Request.Builder()
                            .header(X_FIREBASE_TOKEN, idToken!!)
                            .url(baseUrl + url)
                            .get()
                            .build()

                        val call = client.newCall(request)
                        call.enqueue(callBack)
                    } else {
                        Log.d("token", "NO")
                    }
                }
            })
    }

    fun httpDelete(url: String, callBack: Callback) {
        val mUser = FirebaseAuth.getInstance().currentUser ?: return
        mUser!!.getIdToken(true)
            .addOnCompleteListener(object : OnCompleteListener<GetTokenResult> {
                override fun onComplete(task: Task<GetTokenResult>) {
                    if (task.isSuccessful()) {
                        val idToken = task.getResult()?.getToken()
                        Log.d("token", idToken)
                        val request = Request.Builder()
                            .header("User-Agent", "AndroidApp")
                            .header(X_FIREBASE_TOKEN, idToken!!)
                            .url(baseUrl + url)
                            .delete()
                            .build()

                        val call = client.newCall(request)
                        call.enqueue(callBack)
                    } else {
                        Log.d("token", "NO")
                    }
                }
            })

    }

    fun httpPost(url: String, json: JSONObject, callBack: Callback) {
        val mUser = FirebaseAuth.getInstance().currentUser ?: return
        mUser!!.getIdToken(true)
            .addOnCompleteListener(object : OnCompleteListener<GetTokenResult> {
                override fun onComplete(task: Task<GetTokenResult>) {
                    if (task.isSuccessful()) {
                        val idToken = task.getResult()?.getToken()
                        Log.d("token", idToken)
                        val body = RequestBody.create(JSON, json.toString())

                        Log.d("POST", json.toString())

                        val request = Request.Builder()
                            .header(X_FIREBASE_TOKEN, idToken!!)
                            .url(baseUrl + url)
                            .post(body)
                            .build()

                        val call = client.newCall(request)
                        call.enqueue(callBack)
                    } else {
                        Log.d("token", "NO")
                    }
                }
            })

    }

    fun httpPut(url: String, json: JSONObject, callBack: Callback) {
        val mUser = FirebaseAuth.getInstance().currentUser ?: return
        mUser!!.getIdToken(true)
            .addOnCompleteListener(object : OnCompleteListener<GetTokenResult> {
                override fun onComplete(task: Task<GetTokenResult>) {
                    if (task.isSuccessful()) {
                        val idToken = task.getResult()?.getToken()
                        Log.d("token", idToken)
                        val body = RequestBody.create(JSON, json.toString())

                        val request = Request.Builder()
                            .header(X_FIREBASE_TOKEN, idToken!!)
                            .url(baseUrl + url)
                            .put(body)
                            .build()

                        val call = client.newCall(request)
                        call.enqueue(callBack)
                    } else {
                        Log.d("token", "NO")
                    }
                }
            })

    }

    fun httpPostWithFile(url: String, json: JSONObject, file: File, ext: String, callBack: Callback) {
        val mUser = FirebaseAuth.getInstance().currentUser ?: return
        mUser!!.getIdToken(true)
            .addOnCompleteListener(object : OnCompleteListener<GetTokenResult> {
                override fun onComplete(task: Task<GetTokenResult>) {
                    if (task.isSuccessful()) {
                        val idToken = task.getResult()?.getToken()
                        Log.d("token", idToken)
                        val MEDIA_TYPE = ("jpg/pdf/txt/mp3").toMediaType()

                        val req = MultipartBody.Builder().setType(MultipartBody.FORM)
                            .addFormDataPart(X_FIREBASE_TOKEN, idToken!!)
                            .addFormDataPart("body", json.toString())
                            .addFormDataPart(
                                "file",
                                "file." + ext,
                                RequestBody.create(MEDIA_TYPE, file)
                            ).build()

                        val request = Request.Builder()
                            .url(baseUrl + url)
                            .post(req)
                            .build()

                        val call = client.newCall(request)
                        call.enqueue(callBack)
                    } else {
                        Log.d("token", "NO")
                    }
                }
            })

    }

    fun httpDownload(url: String, callBack: Callback) {
        val mUser = FirebaseAuth.getInstance().currentUser ?: return
        mUser!!.getIdToken(true)
            .addOnCompleteListener(object : OnCompleteListener<GetTokenResult> {
                override fun onComplete(task: Task<GetTokenResult>) {
                    if (task.isSuccessful()) {
                        val idToken = task.getResult()?.getToken()
                        Log.d("token", idToken)
                        val request = Request.Builder()
                            .header("User-Agent", "AndroidApp")
                            .header(X_FIREBASE_TOKEN, idToken!!)
                            .url(baseUrl + url)
                            .get()
                            .build()

                        val call = client.newCall(request)
                        call.enqueue(callBack)
                    } else {
                        Log.d("token", "NO")
                    }
                }
            })

    }
}
