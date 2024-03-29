package com.mcc_project_5

import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.ListView
import android.widget.SearchView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import com.google.firebase.auth.FirebaseAuth
import com.mcc_project_5.Adapters.UserListAdapter
import com.mcc_project_5.DataModels.User
import com.mcc_project_5.Tools.Requester
import kotlinx.android.synthetic.main.activity_sign_up.*
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Response
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.*
import kotlin.Comparator

class AddUserActivity : AppCompatActivity() {
    private val users  =  arrayListOf<User>()
    private val visibleUsers = arrayListOf<User>()
    private val checkedUsers = arrayListOf<String>()
    var projectId = ""
    var title = ""

    private enum class SortOrder {
        ASC, DESC
    }

    private var sortOrder: SortOrder = SortOrder.DESC

    class ComparatorByName: Comparator<User>{
        override fun compare(o1: User?, o2: User?): Int {
            if(o1 == null || o2 == null){
                return 0;
            }
            return o1.name.compareTo(o2.name)
        }
    }

    fun performSorting() {
        Collections.sort(visibleUsers, ComparatorByName())
        if (sortOrder == SortOrder.DESC)
            visibleUsers.reverse()
        refreshUserList()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.users_list_activity)

        val mUser = FirebaseAuth.getInstance().currentUser ?: finish()

        projectId = this.intent.getStringExtra("projectId")
        title = this.intent.getStringExtra("title")
        val toolbar = findViewById<Toolbar>(R.id.toolbar)
        toolbar.inflateMenu(R.menu.project_content_general)
        toolbar.setTitle(title)
        setSupportActionBar(toolbar)

        val userListAdapter = UserListAdapter(projectId!!)
        userListAdapter.setItems(visibleUsers)
        val usersListView = findViewById<ListView>(R.id.usersListView)
        usersListView.adapter = userListAdapter

        loadUsersTemplate()
    }

    fun refreshUserList() {
        val adapter = findViewById<ListView>(R.id.usersListView).adapter as UserListAdapter
        adapter.notifyDataSetChanged()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        super.onCreateOptionsMenu(menu)
        val inflater = menuInflater
        inflater.inflate(R.menu.users_list_general, menu)
        //inflater.inflate(R.menu.filter, menu)

        val searchView = menu.findItem(R.id.action_search).actionView as SearchView
        searchView.setOnQueryTextListener(object: SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean {
                return false
            }

            override fun onQueryTextChange(newText: String?): Boolean {
                //if (newText!!.length < 5) {
                //    return true
                //}
                visibleUsers.clear()
                users.forEach {
                    if (it.name.contains(newText!!, true)) {
                        visibleUsers.add(it)
                    }
                }
                runOnUiThread {
                    refreshUserList()
                }
                return true
            }

        })
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.title == "refresh") {
            loadUsersTemplate()
        } else if (item.title == "sort") {
            if (sortOrder == SortOrder.DESC) {
                item.setIcon(R.drawable.ic_sort_reversed_black_24dp)
                item.icon.layoutDirection = View.LAYOUT_DIRECTION_RTL
                sortOrder = SortOrder.ASC
                performSorting()
            } else {
                item.setIcon(R.drawable.ic_sort_black_24dp)
                item.icon.layoutDirection = View.LAYOUT_DIRECTION_LTR
                sortOrder = SortOrder.DESC
                performSorting()
            }
        }

        return true
    }

    fun addMembersProject(v: View) {
        val requester = Requester(baseContext)
        val json= JSONObject()
        checkedUsers.clear()
        users.forEach {
            if (it.checked) {
                checkedUsers.add(it.id)
            }
        }
        json.put("members", JSONArray(checkedUsers))
        Log.d("members", checkedUsers.toString())
        requester.httpPost("project/$projectId/members/set", json,  object: Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.d("DDD", "FAIL")
                return
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    Log.d("DDD","OK" + response.message)
                    finish()
                } else {
                    Log.d("DDD","NOT OK" + response.message)
                    return
                }
            }
        })
    }


    fun loadUsersTemplate() {
        val requester = Requester(baseContext)
        requester.httpGet("users", object: Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.d("DDD", "FAIL")
                return
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val resultJson = response.body!!.string()
                    val json = JSONArray(resultJson)
                    users.clear()
                    for(i in 0 until json.length()) {
                        val item = json.getJSONObject(i)
                        val user = User(item)
                        users.add(user)
                    }
                    visibleUsers.clear()
                    visibleUsers.addAll(users)
                    runOnUiThread {
                        performSorting()
                        refreshUserList()
                    }
                } else {
                    return
                }
            }
        })

    }
}