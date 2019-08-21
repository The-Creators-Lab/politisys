"use strict";

// Load plugins
const autoprefixer = require("gulp-autoprefixer");
const browsersync = require("browser-sync").create();
const cleanCSS = require("gulp-clean-css");
const del = require("del");
const gulp = require("gulp");
const header = require("gulp-header");
const merge = require("merge-stream");
const plumber = require("gulp-plumber");
const rename = require("gulp-rename");
const sass = require("gulp-sass");

const staticFolder = "./staticfiles/";

// Load package.json for banner
const pkg = require('./package.json');

// Set the banner content
const banner = ['/*!\n',
  ' * Start Bootstrap - <%= pkg.title %> v<%= pkg.version %> (<%= pkg.homepage %>)\n',
  ' * Copyright 2013-' + (new Date()).getFullYear(), ' <%= pkg.author %>\n',
  ' * Licensed under <%= pkg.license %> (https://github.com/BlackrockDigital/<%= pkg.name %>/blob/master/LICENSE)\n',
  ' */\n',
  '\n'
].join('');

// BrowserSync
function browserSync(done) {
  browsersync.init({
    server: {
      baseDir: "./"
    },
    port: 3000
  });
  done();
}

// BrowserSync reload
function browserSyncReload(done) {
  browsersync.reload();
  done();
}

// Clean vendor
function clean() {
  return del([staticFolder]);
}

// Bring third party dependencies from node_modules into vendor directory
function modules() {
  // Bootstrap
  var bootstrap = gulp.src('./node_modules/bootstrap/dist/**/*')
    .pipe(gulp.dest(`./${staticFolder}/bootstrap`));
  // Font Awesome CSS
  var fontAwesomeCSS = gulp.src('./node_modules/@fortawesome/fontawesome-free/css/**/*')
    .pipe(gulp.dest(`./${staticFolder}/fontawesome-free/css`));
  // Font Awesome Webfonts
  var fontAwesomeWebfonts = gulp.src('./node_modules/@fortawesome/fontawesome-free/webfonts/**/*')
    .pipe(gulp.dest(`./${staticFolder}/fontawesome-free/webfonts`));
  // jQuery Easing
  var jqueryEasing = gulp.src('./node_modules/jquery.easing/*.js')
    .pipe(gulp.dest(`./${staticFolder}/jquery-easing`));
  // jQuery
  var jquery = gulp.src([
    './node_modules/jquery/dist/*',
    '!./node_modules/jquery/dist/core.js'
  ])
    .pipe(gulp.dest(`./${staticFolder}/jquery`));

  var highCharts = gulp.src("./node_modules/highcharts/**/*")
    .pipe(gulp.dest(`./${staticFolder}/highcharts`));

  // Simple Line Icons
  var simpleLineIconsFonts = gulp.src('./node_modules/simple-line-icons/fonts/**')
    .pipe(gulp.dest(`./${staticFolder}/simple-line-icons/fonts`));
  var simpleLineIconsCSS = gulp.src('./node_modules/simple-line-icons/css/**')
    .pipe(gulp.dest(`./${staticFolder}/simple-line-icons/css`));
  return merge(
    bootstrap,
    fontAwesomeCSS, fontAwesomeWebfonts,
    jquery, jqueryEasing,
    highCharts,
    simpleLineIconsFonts, simpleLineIconsCSS);
}

// CSS task
function css() {
  return gulp
    .src("./templates/scss/**/*.scss")
    .pipe(plumber())
    .pipe(sass({
      outputStyle: "expanded",
      includePaths: "./node_modules",
    }))
    .on("error", sass.logError)
    .pipe(autoprefixer({
      browsers: ['last 2 versions'],
      cascade: false
    }))
    .pipe(header(banner, {
      pkg: pkg
    }))
    .pipe(gulp.dest(`./${staticFolder}/css`))
    .pipe(rename({
      suffix: ".min"
    }))
    .pipe(cleanCSS())
    .pipe(gulp.dest(`./${staticFolder}/css`))
    .pipe(browsersync.stream());
}

function images() {
  return gulp
    .src("./templates/img/*")
    .pipe(gulp.dest(`./${staticFolder}/img`))
}

// Watch files
function watchFiles() {
  gulp.watch("./templates/scss/**/*", css);
  gulp.watch("./**/*.html", browserSyncReload);
}

// Define complex tasks
const vendor = gulp.series(clean, modules);
const build = gulp.series(vendor, css, images);
const watch = gulp.series(build, gulp.parallel(watchFiles, browserSync));

// Export tasks
exports.css = css;
exports.clean = clean;
exports.vendor = vendor;
exports.build = build;
exports.watch = watch;
exports.default = build;