# FlavorVault

Welcome to FlavorVault, the ultimate recipe database for all ages. Discover easy, delicious recipes that make cooking fun and accessible. From quick weeknight dinners to impressive dishes for special occasions, FlavorVault has something for everyone. Join our community and start your culinary adventure today!

### Link to live site : [FlavorVault](https://flavorvault-d681a47fade4.herokuapp.com)

## User Experience (UX)

### Initial Discussion

FlavorVault is a online recipe database that is focused towards all ages who are looking to step up there cooking game from home and create easy yet tasty meals, without breaking a sweat.

The site is designed to be a simple and easy to use recipe database that allows users to add, view, edit and delete recipes.

### User Stories

#### Client Goals

-   To be able to view the site on a range of devices.
-   To make it easy for users to find and follow recipes.
-   To allow users to add, view, edit and delete recipes.
-   To allow people to contact FlavorVault to ask further questions or suggest cooking recommendations etc.

#### First Time User Goals

-   I want to find out what FlavorVault is about and what i can do.
-   I want to be able to navigate the site easily.
-   I want to see all the social media links.
-   I want to be able to view the site and recipes on any device I am using.

#### Returning User Goals

-   I want to easily navigate to my favorite recipes.
-   I want to keep up to date with any new social media they post.

## Design

### Colour Scheme

I used the site [coolors](https://coolors.co/palette/ccd5ae-e9edc9-fefae0-faedcd-d4a373) for the color scheme, I think these colors complement the purpose of the site well.

![Color Scheme](/assets/screenshots/coolors.png)

### Imagery

I have used high quality images of food to compliment the site, all my images are sourced from [unsplash](https://unsplash.com/images/stock).

### Favicon

I used [Favicon](https://favicon.io/) to create my favicon.

### Wireframes

I used [Balsamiq](https://balsamiq.com/) for my wireframes.

![FlavorVault Wireframes](/assets/screenshots/wireframes.png)

## Features

The website is comprised of five main pages, all are accessible from the navigation menu (home page, recipes page, categories page, login page & signup page).  
And two secondary pages. (recipe page & recipe form page).  
Lastly one extra page. (404 page)

#### All Pages on the website have:

-   A responsive navigation bar at the top which allows the user to navigate through the site. To the left of the navigation bar is the text FlavorVault. To the right of the navigation bar are the links to the website pages (home page, recipes page, categories page, login page & signup page). When viewing on mobile devices the navigation links change to a burger toggler. This was implemented to give the site a clean look and to promote a good user experience, as users are used to seeing the burger icon when navigating a site on a mobile device.

-   A footer which contains social media icons links to Instagram and Facebook. Icons were used to keep the footer clean and because they are universally recognizable.

### General features on each page

Each page has the same header and footer as well as theme to complete.

#### Home Page

![FlavorVault Home page](/assets/screenshots/home.png)

#### Recipes Page

![FlavorVault Recipes page](/assets/screenshots/recipe.png)

#### Categories Page

![FlavorVault Categories page](/assets/screenshots/categories.png)

#### Login Page

![FlavorVault Login page](/assets/screenshots/login.png)

#### Signup Page

![FlavorVault Signup page](/assets/screenshots/signup.png)

#### Profile Page

![FlavorVault Profile page](/assets/screenshots/profile.png)

## Technologies Used

### Languages Used

Languages used HTML & CSS & Python & JavaScript

### Frameworks, Libraries & Programs Used

Balsamiq - Used to create wireframes.

Flask - Used to create the backend for the website.

Flask-WTF - Used to create the forms for the website.

Flask-Login - Used to create the login system for the website.

Jinja - Used to create the dynamic pages for the website.

Heroku - Used to deploy the website.

MongoDB - Used to store the data for the website.

dnspython - Used to connect to the database.

jQuery - Used to make the site more interactive.

Font Awesome - For icons.

pymongo - Used to interact with the database.

Git - For version control.

Github - To save and store the files for the website.

Materialize - Used to create the navigation bar, cards and form.

Google Dev Tools - To troubleshoot and test features and solve issues with responsiveness and styling.

Fontawesome - For icons.

## Deployment & Local Development

### Deployment

The site is deployed using Heroku - [FlavorVault](https://flavorvault-d681a47fade4.herokuapp.com)

To Deploy the site using Heroku:

1. Create a `requirements.txt` file using the terminal command `pip freeze > requirements.txt`

2. Create a `Procfile` with the terminal command `echo web: python app.py > Procfile`

3. Login to Heroku and create a new app by clicking "New" and "Create new app"

4. Choose a name for your app (must be unique) and select your region

5. From the deploy tab on Heroku:

    - Select "Connect to GitHub" as the deployment method
    - Search for your repository name and click "Connect"
    - Scroll to the bottom of the deploy page and select "Enable Automatic Deploys"

6. Set up your environment variables in Heroku:

    - Click the settings tab
    - Click "Reveal Config Vars"
    - Add any necessary environment variables (e.g., SECRET_KEY, DATABASE_URL)

7. Push these changes to your GitHub repository: `bash
git add . 
git commit -m "Deployment: Add requirements.txt and Procfile"
git push   `

8. Your app will now be deployed to Heroku and will update automatically each time you push changes to GitHub

### Local Development

#### How to Fork

To fork the repository:

1. Log in (or sign up) to Github.
2. Go to the repository for this project, [FlavorVault](https://github.com/EthanPeters96/FlavorVault)
3. Click the Fork button in the top right corner.

#### How to Clone

To clone the repository:

1. Log in (or sign up) to GitHub.
2. Go to the repository for this project, [FlavorVault](https://github.com/EthanPeters96/FlavorVault)
3. Click on the code button, select whether you would like to clone with HTTPS, SSH or GitHub CLI and copy the link shown.
4. Open the terminal in your code editor and change the current working directory to the location you want to use for the cloned directory.
5. Type 'git clone' into the terminal and then paste the link you copied in step 3. Press enter.

## Testing

### Jest Testing

I have written a testing script using jest, the test pass

![Jest](/assets/screenshots/jest.png)

### Manual Testing

| Feature         | Action                                | Expected result                                   | Tested | Passed | Comments |
| --------------- | ------------------------------------- | ------------------------------------------------- | ------ | ------ | -------- |
| Home            | Click on the "Home" link              | The user is redirected to the main page           | Yes    | Yes    | -        |
| New Recipes     | Click on the "New Recipes" link       | The user is redirected to the recipes page        | Yes    | Yes    | -        |
| Login           | Click on the "Login" link             | The user is redirected to the login page          | Yes    | Yes    | -        |
| Register        | Click on the "Register" link          | The user is redirected to the register page       | Yes    | Yes    | -        |
| Logout          | Click on the "Logout" link            | The user is redirected to the logout page         | Yes    | Yes    | -        |
| Profile         | Click on the "Profile" link           | The user is redirected to the profile page        | Yes    | Yes    | -        |
| Add Recipe      | Click on the "Add Recipe" button      | The user is redirected to the add recipe page     | Yes    | Yes    | -        |
| Edit Recipe     | Click on the "Edit Recipe" button     | The user is redirected to the edit recipe page    | Yes    | Yes    | -        |
| Delete Recipe   | Click on the "Delete" button          | Modal appears asking for confirmation             | Yes    | Yes    | -        |
| Delete Recipe   | Click "Cancel" in delete modal        | Modal closes, recipe is not deleted               | Yes    | Yes    | -        |
| Delete Recipe   | Click "Delete" in delete modal        | Recipe is deleted and user sees success message   | Yes    | Yes    | -        |
| Add Category    | Click on the "Add Category" button    | The user is redirected to the add category page   | Yes    | Yes    | -        |
| View Category   | Click on the "View Category" button   | The user is redirected to the view category page  | Yes    | Yes    | -        |
| Edit Category   | Click on the "Edit Category" button   | The user is redirected to the edit category page  | Yes    | Yes    | -        |
| Delete Category | Click on the "Delete Category" button | Modal appears asking for confirmation             | Yes    | Yes    | -        |
| Delete Category | Click "Cancel" in delete modal        | Modal closes, category is not deleted             | Yes    | Yes    | -        |
| Delete Category | Click "Delete" in delete modal        | Category is deleted and user sees success message | Yes    | Yes    | -        |

The site was also tested using dev tools on Google Chrome for responsiveness.

Favicon does not work on live site however does work on local deployment.

I was unable to test 404 page.

### LightHouse

I have tested my website using lighthouse.

#### Home Page

![Home Page](#)

#### Recipes Page

![Recipes](#)

#### About Page

![About](#)

#### Contact Page

![Contact](#)

#### Tacos Page

![Tacos](#)

#### Carbonara Page

![Carbonara](#)

### Compatibility

Tested on [Google Chrome](https://www.google.co.uk/) for functionality , appearance and responsiveness. All features passed.

### Validator

I have used [W3C](https://www.w3.org/) & [JSHint](https://jshint.com/) to validate my code.

### HTML

![HTML](/assets/screenshots/html-val.png)

Tested all pages.

### CSS

![CSS](/assets/screenshots/css-val.png)

### JS

![JS](/assets/screenshots/js-hint.png)

## Credits

I have used previous projects to help with this project.

I used AI assistance for my script.js file. and my app.py file.

[flask-task-manager](https://github.com/Code-Institute-Solutions/TaskManagerAuth)

[Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/quickstart/)

I also referred to [Materialize](https://materializecss.com/) docs to learn new ways to style my page.

I followed some guidance from my mentor [Graeme Taylor](https://github.com/G-Taylor).

### Media

Stock images are sourced from [Usplash](https://unsplash.com/).

### Acknowledgments

I'd like to give thanks to Graeme my mentor for the support he has given me throughout my project here is a [link](https://github.com/G-Taylor) to his github.

I'd also like to thank my tutor Jonathan from Nescot.
